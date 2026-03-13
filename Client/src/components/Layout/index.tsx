import type { PropsWithChildren } from "react";
import "./layout.scss";

function Layout({ children }: PropsWithChildren): JSX.Element {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__inner">
          <h1>SOP Workflow Generator</h1>
        </div>
      </header>
      <main className="app-main">
        <div className="app-main__inner">{children}</div>
      </main>
    </div>
  );
}

export default Layout;
