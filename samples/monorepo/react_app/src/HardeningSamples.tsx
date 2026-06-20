// Intentionally insecure sample code -- Waypoint test fixture. Do not deploy.
// Plants for the waypoint-react-* hardening rules (proxy detectors).
import React, { useState, useEffect, useRef } from "react";

interface Props {
  url: string;
  htmlBlob: string;
  items: string[];
  initialName: string;
  rawConfig: string;
}

// ----------------------------------------------------------------------------
// SECURITY
// ----------------------------------------------------------------------------

export function LinkCard({ url, htmlBlob }: Props) {
  return (
    <div>
      {/* WAYPOINT-PLANT: waypoint-react-unsafe-href [axes: security] */}
      <a href={url}>profile</a>

      {/* WAYPOINT-PLANT: waypoint-react-unsafe-href [axes: security] */}
      <img src={url} alt="avatar" />

      {/* WAYPOINT-OK: constant href is a static literal, not attacker-controlled */}
      <a href="/about">about</a>

      {/* WAYPOINT-PLANT: waypoint-react-target-blank-no-noopener [axes: security] */}
      <a href={url} target="_blank">
        external
      </a>

      {/* WAYPOINT-OK: target=_blank with rel=noopener closes the tabnabbing hole */}
      <a href={url} target="_blank" rel="noopener noreferrer">
        external safe
      </a>

      {/* WAYPOINT-PLANT: waypoint-react-create-markup-helper [axes: security] */}
      <div dangerouslySetInnerHTML={createMarkup(htmlBlob)} />
    </div>
  );
}

// WAYPOINT-PLANT: waypoint-react-create-markup-helper [axes: security]
function createMarkup(dirty: string) {
  return { __html: dirty };
}

// WAYPOINT-OK: constant html payload, no untrusted input
function safeMarkup() {
  return { __html: "<b>static</b>" };
}

export function SpreadButton(props: Props) {
  const attrs: any = props;
  return (
    <div>
      {/* WAYPOINT-PLANT: waypoint-react-untrusted-prop-spread [axes: security,abuse] */}
      <button {...attrs}>click</button>

      {/* WAYPOINT-OK: explicit, whitelisted props only */}
      <button type="button" disabled={false}>
        click
      </button>
    </div>
  );
}

// ----------------------------------------------------------------------------
// EDGE-CASE
// ----------------------------------------------------------------------------

export function ItemList({ items }: Props) {
  return (
    <ul>
      {items.map((item, i) => {
        // WAYPOINT-PLANT: waypoint-react-array-index-key [axes: edge-case]
        return <li key={i}>{item}</li>;
      })}
      {/* WAYPOINT-PLANT: waypoint-react-array-index-key [axes: edge-case] */}
      {items.map((item, idx) => (
        <li key={idx + 1}>{item}</li>
      ))}
    </ul>
  );
}

export function ItemListNoKey({ items }: Props) {
  return (
    <ul>
      {/* WAYPOINT-PLANT: waypoint-react-map-no-key [axes: edge-case] */}
      {items.map((item) => (
        <li>{item}</li>
      ))}
    </ul>
  );
}

export function ItemListOk({ items }: Props) {
  return (
    <ul>
      {/* WAYPOINT-OK: stable, content-derived key */}
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export function Mutator({ items }: Props) {
  // WAYPOINT-PLANT: waypoint-react-usestate-from-prop [axes: edge-case]
  const [list, setList] = useState<string[]>(items);
  const cache = useRef<{ count: number }>({ count: 0 });

  function add(x: string) {
    // WAYPOINT-PLANT: waypoint-react-direct-state-mutation [axes: edge-case]
    list.push(x);
    // WAYPOINT-PLANT: waypoint-react-direct-state-mutation [axes: edge-case]
    cache.current.count = cache.current.count + 1;
  }

  function addOk(x: string) {
    // WAYPOINT-OK: immutable update via the setter
    setList((prev) => [...prev, x]);
  }

  add("a");
  addOk("b");
  return <p>{list.length}</p>;
}

export function StaleSeed({ initialName }: Props) {
  // WAYPOINT-PLANT: waypoint-react-usestate-from-prop [axes: edge-case]
  const [name, setName] = useState(initialName);

  // WAYPOINT-OK: literal initial value, no frozen-prop hazard
  const [count, setCount] = useState(0);

  return (
    <div onClick={() => setCount(count + 1)}>
      {name}: {count}
    </div>
  );
}

export function Clock() {
  // WAYPOINT-PLANT: waypoint-react-nondeterministic-render [axes: edge-case]
  const id = Math.random();
  // WAYPOINT-PLANT: waypoint-react-nondeterministic-render [axes: edge-case]
  const now = new Date();
  return (
    <div data-id={id}>
      rendered at {now.toISOString()}
    </div>
  );
}

// ----------------------------------------------------------------------------
// ABUSE
// ----------------------------------------------------------------------------

function Child(_props: { onClick: () => void; style: object; rows: number[] }) {
  return <span>child</span>;
}

export function Parent({ items }: Props) {
  return (
    <div>
      {/* WAYPOINT-PLANT: waypoint-react-inline-prop-literal [axes: abuse] */}
      <Child onClick={() => console.log("hi")} style={{ color: "red" }} rows={[1, 2, 3]} />

      {/* WAYPOINT-PLANT: waypoint-react-heavy-work-in-render [axes: abuse] */}
      <p>{items.filter((x) => new RegExp("^a").test(x)).length}</p>
    </div>
  );
}

export function HeavyRender({ rawConfig, items }: Props) {
  // WAYPOINT-PLANT: waypoint-react-heavy-work-in-render [axes: abuse]
  const parsed = JSON.parse(rawConfig);
  // WAYPOINT-PLANT: waypoint-react-heavy-work-in-render [axes: abuse]
  const sorted = items.sort();
  return (
    <p>
      {parsed.k}-{sorted.length}
    </p>
  );
}

// ----------------------------------------------------------------------------
// CONCURRENCY
// ----------------------------------------------------------------------------

export function Ticker() {
  const [n, setN] = useState(0);

  // WAYPOINT-PLANT: waypoint-react-timer-in-effect-no-cleanup [axes: concurrency,edge-case]
  useEffect(() => {
    setInterval(() => {
      setN((v) => v + 1);
    }, 1000);
  }, []);

  // WAYPOINT-OK: interval cleared on unmount
  useEffect(() => {
    const id = setInterval(() => setN((v) => v + 1), 1000);
    return () => clearInterval(id);
  }, []);

  return <p>{n}</p>;
}

export function Resizer() {
  const [w, setW] = useState(0);

  // WAYPOINT-PLANT: waypoint-react-listener-in-effect-no-cleanup [axes: concurrency,edge-case]
  useEffect(() => {
    window.addEventListener("resize", () => setW(window.innerWidth));
  }, []);

  // WAYPOINT-OK: listener removed in cleanup
  useEffect(() => {
    const onResize = () => setW(window.innerWidth);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return <p>{w}</p>;
}
