// Intentionally insecure CDK sample -- Waypoint IaC test fixture. Do not deploy.
// Each `// WAYPOINT-PLANT: <rule-id>` comment precedes a construct that should fire
// that rule; adjacent `// WAYPOINT-OK:` blocks are safe counterparts that should
// NOT fire. Imports may be unused; the file only needs to parse and be scannable.
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as iam from "aws-cdk-lib/aws-iam";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as rds from "aws-cdk-lib/aws-rds";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as logs from "aws-cdk-lib/aws-logs";
import * as ecs from "aws-cdk-lib/aws-ecs";

export class DataPlatformStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ----------------------------------------------------------------- S3
    // WAYPOINT-PLANT: waypoint-ts-cdk-s3-no-encryption
    // WAYPOINT-PLANT: waypoint-ts-cdk-s3-no-versioning
    const rawBucket = new s3.Bucket(this, "RawLandingBucket", {
      bucketName: "raw-landing",
    });

    // WAYPOINT-PLANT: waypoint-ts-cdk-s3-public
    const publicBucket = new s3.Bucket(this, "PublicBucket", {
      publicReadAccess: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ACLS,
    });

    // WAYPOINT-PLANT: waypoint-ts-cdk-destructive-removal-policy
    const scratchBucket = new s3.Bucket(this, "ScratchBucket", {
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // WAYPOINT-OK: encrypted + versioned + retained data bucket (PIT-safe)
    const curatedBucket = new s3.Bucket(this, "CuratedBucket", {
      encryption: s3.BucketEncryption.KMS_MANAGED,
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // ----------------------------------------------------------------- IAM
    // WAYPOINT-PLANT: waypoint-ts-cdk-iam-wildcard
    const adminPolicy = new iam.PolicyStatement({
      actions: ["*"],
      resources: ["*"],
    });

    // WAYPOINT-PLANT: waypoint-ts-cdk-iam-wildcard
    const broadActions = new iam.PolicyStatement({
      actions: ["*"],
      resources: ["arn:aws:s3:::curated/*"],
    });

    // WAYPOINT-OK: scoped IAM — specific actions, specific resource
    const scopedPolicy = new iam.PolicyStatement({
      actions: ["s3:GetObject", "s3:PutObject"],
      resources: ["arn:aws:s3:::curated/*"],
    });

    // ----------------------------------------------------------------- EC2 / SG
    const vpc = new ec2.Vpc(this, "Vpc", { maxAzs: 2 });
    const sg = new ec2.SecurityGroup(this, "Sg", { vpc });

    // WAYPOINT-PLANT: waypoint-ts-cdk-sg-open-world
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), "ssh world");

    // WAYPOINT-PLANT: waypoint-ts-cdk-sg-open-world
    sg.connections.allowFrom(ec2.Peer.anyIpv4(), ec2.Port.tcp(5432));

    // WAYPOINT-OK: ingress restricted to an internal CIDR
    sg.addIngressRule(ec2.Peer.ipv4("10.0.0.0/16"), ec2.Port.tcp(22), "ssh vpc");

    // ----------------------------------------------------------------- RDS
    // WAYPOINT-PLANT: waypoint-ts-cdk-db-no-encryption
    // WAYPOINT-PLANT: waypoint-ts-cdk-db-public
    const analyticsDb = new rds.DatabaseInstance(this, "AnalyticsDb", {
      engine: rds.DatabaseInstanceEngine.POSTGRES,
      vpc,
      publiclyAccessible: true,
    });

    // WAYPOINT-OK: encrypted, private RDS instance
    const secureDb = new rds.DatabaseInstance(this, "SecureDb", {
      engine: rds.DatabaseInstanceEngine.POSTGRES,
      vpc,
      storageEncrypted: true,
      publiclyAccessible: false,
    });

    // ----------------------------------------------------------------- ECS env secret
    // WAYPOINT-PLANT: waypoint-ts-cdk-secret-literal-env
    const taskDef = new ecs.FargateTaskDefinition(this, "Task");
    taskDef.addContainer("app", {
      image: ecs.ContainerImage.fromRegistry("internal/app:latest"),
      environment: {
        DB_HOST: "analytics.internal",
        DB_PASSWORD: "s3cr3t-litera1-passw0rd",
      },
    });

    // WAYPOINT-OK: secret pulled from Secrets Manager, not a literal env value
    taskDef.addContainer("app-secure", {
      image: ecs.ContainerImage.fromRegistry("internal/app:latest"),
      environment: {
        DB_HOST: "analytics.internal",
      },
    });

    // ----------------------------------------------------------------- Logs
    // WAYPOINT-PLANT: waypoint-ts-cdk-log-retention-infinite
    // WAYPOINT-PLANT: waypoint-ts-cdk-destructive-removal-policy
    const auditLogs = new logs.LogGroup(this, "AuditLogs", {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // WAYPOINT-OK: explicit retention window
    const keptLogs = new logs.LogGroup(this, "KeptLogs", {
      retention: logs.RetentionDays.ONE_YEAR,
    });

    // ----------------------------------------------------------------- DynamoDB
    // WAYPOINT-PLANT: waypoint-ts-cdk-destructive-removal-policy
    const ticksTable = new dynamodb.Table(this, "TicksTable", {
      partitionKey: { name: "pk", type: dynamodb.AttributeType.STRING },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
  }
}
