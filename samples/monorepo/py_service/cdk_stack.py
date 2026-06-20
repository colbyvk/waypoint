# Intentionally insecure CDK sample -- Waypoint IaC test fixture. Do not deploy.
# Each `# WAYPOINT-PLANT: <rule-id>` comment precedes a construct that should fire
# that rule; adjacent `# WAYPOINT-OK:` blocks are safe counterparts that should NOT
# fire. Imports may be unused; the file only needs to parse and be scannable.
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_redshift as redshift,
    aws_dynamodb as dynamodb,
    aws_logs as logs,
    aws_ecs as ecs,
    Stack,
)
from constructs import Construct


class DataPlatformStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs) -> None:
        super().__init__(scope, cid, **kwargs)

        # ------------------------------------------------------------- S3
        # WAYPOINT-PLANT: waypoint-py-cdk-s3-no-encryption
        # WAYPOINT-PLANT: waypoint-py-cdk-s3-no-versioning
        raw_bucket = s3.Bucket(self, "RawLandingBucket")

        # WAYPOINT-PLANT: waypoint-py-cdk-s3-public
        public_bucket = s3.Bucket(
            self,
            "PublicBucket",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
        )

        # WAYPOINT-PLANT: waypoint-py-cdk-destructive-removal-policy
        scratch_bucket = s3.Bucket(
            self,
            "ScratchBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # WAYPOINT-OK: encrypted + versioned + retained data bucket (PIT-safe)
        curated_bucket = s3.Bucket(
            self,
            "CuratedBucket",
            encryption=s3.BucketEncryption.KMS_MANAGED,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # ------------------------------------------------------------- IAM
        # WAYPOINT-PLANT: waypoint-py-cdk-iam-wildcard
        admin_policy = iam.PolicyStatement(
            actions=["*"],
            resources=["*"],
        )

        # WAYPOINT-PLANT: waypoint-py-cdk-iam-wildcard
        broad_actions = iam.PolicyStatement(
            actions=["*"],
            resources=["arn:aws:s3:::curated/*"],
        )

        # WAYPOINT-OK: scoped IAM — specific actions, specific resource
        scoped_policy = iam.PolicyStatement(
            actions=["s3:GetObject", "s3:PutObject"],
            resources=["arn:aws:s3:::curated/*"],
        )

        # ------------------------------------------------------------- EC2 / SG
        vpc = ec2.Vpc(self, "Vpc", max_azs=2)
        sg = ec2.SecurityGroup(self, "Sg", vpc=vpc)

        # WAYPOINT-PLANT: waypoint-py-cdk-sg-open-world
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "ssh world")

        # WAYPOINT-PLANT: waypoint-py-cdk-sg-open-world
        sg.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(5432))

        # WAYPOINT-OK: ingress restricted to an internal CIDR
        sg.add_ingress_rule(ec2.Peer.ipv4("10.0.0.0/16"), ec2.Port.tcp(22), "ssh vpc")

        # ------------------------------------------------------------- RDS / Redshift
        # WAYPOINT-PLANT: waypoint-py-cdk-db-no-encryption
        # WAYPOINT-PLANT: waypoint-py-cdk-db-public
        analytics_db = rds.DatabaseInstance(
            self,
            "AnalyticsDb",
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            vpc=vpc,
            publicly_accessible=True,
        )

        # WAYPOINT-PLANT: waypoint-py-cdk-db-no-encryption
        warehouse = redshift.Cluster(
            self,
            "Warehouse",
            master_user=redshift.Login(master_username="admin"),
            vpc=vpc,
        )

        # WAYPOINT-OK: encrypted, private RDS instance
        secure_db = rds.DatabaseInstance(
            self,
            "SecureDb",
            engine=rds.DatabaseInstanceEngine.POSTGRES,
            vpc=vpc,
            storage_encrypted=True,
            publicly_accessible=False,
        )

        # ------------------------------------------------------------- ECS env secret
        # WAYPOINT-PLANT: waypoint-py-cdk-secret-literal-env
        task_def = ecs.FargateTaskDefinition(self, "Task")
        task_def.add_container(
            "app",
            image=ecs.ContainerImage.from_registry("internal/app:latest"),
            environment={
                "DB_HOST": "analytics.internal",
                "DB_PASSWORD": "s3cr3t-litera1-passw0rd",
            },
        )

        # WAYPOINT-OK: secret pulled from Secrets Manager, not a literal env value
        task_def.add_container(
            "app-secure",
            image=ecs.ContainerImage.from_registry("internal/app:latest"),
            environment={"DB_HOST": "analytics.internal"},
        )

        # ------------------------------------------------------------- Logs
        # WAYPOINT-PLANT: waypoint-py-cdk-log-retention-infinite
        # WAYPOINT-PLANT: waypoint-py-cdk-destructive-removal-policy
        audit_logs = logs.LogGroup(
            self,
            "AuditLogs",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # WAYPOINT-OK: explicit retention window
        kept_logs = logs.LogGroup(
            self,
            "KeptLogs",
            retention=logs.RetentionDays.ONE_YEAR,
        )

        # ------------------------------------------------------------- DynamoDB
        # WAYPOINT-PLANT: waypoint-py-cdk-destructive-removal-policy
        ticks_table = dynamodb.Table(
            self,
            "TicksTable",
            partition_key=dynamodb.Attribute(
                name="pk", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
