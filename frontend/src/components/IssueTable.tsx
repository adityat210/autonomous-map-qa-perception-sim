import { Issue } from "../lib/api";

export function IssueTable({ issues }: { issues: Issue[] }) {
  return (
    <section className="table-panel">
      <h2>validation issues</h2>
      {issues.length === 0 ? (
        <p className="empty">no issues match the current filter</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>severity</th>
              <th>type</th>
              <th>explanation</th>
              <th>action</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue) => (
              <tr key={issue.issue_id}>
                <td>
                  <span className={`badge ${issue.severity}`}>{issue.severity}</span>
                </td>
                <td>{issue.issue_type}</td>
                <td>{issue.explanation}</td>
                <td>{issue.recommended_action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
