export default function ErrorState({ message }: { message: string }) {
  return <div className="panel error">{message}</div>;
}
