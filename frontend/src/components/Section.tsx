import type { ReactNode } from "react";

type Props = {
  title: string;
  icon: ReactNode;
  children: ReactNode;
  wide?: boolean;
};

export function Section({ title, icon, children, wide }: Props) {
  return (
    <section className={wide ? "panel wide" : "panel"}>
      <header className="panel-header">
        {icon}
        <h2>{title}</h2>
      </header>
      {children}
    </section>
  );
}
