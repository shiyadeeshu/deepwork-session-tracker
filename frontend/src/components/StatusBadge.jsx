export default function StatusBadge({ status }) {
  return <span className={`badge st-${status}`}>{status}</span>
}
