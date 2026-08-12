type Story = {
  id: number;
  title: string;
  content: string;
  author_name: string;
  status: string;
  submitted_at: string;
};

type Props = {
  story: Story;
  onApprove?: (id: number) => void;
  onDeny?: (id: number) => void;
  onDelete?: (id: number) => void;
};

export default function StoryCard({ story, onApprove, onDeny, onDelete }: Props) {
  return (
    <div className="border rounded-xl p-4 shadow-sm bg-white">
      <h2 className="text-lg font-semibold">{story.title}</h2>
      <p className="text-sm text-gray-500 mb-2">By {story.author_name} · {new Date(story.submitted_at).toLocaleDateString()}</p>
      <p className="text-gray-700 mb-4">{story.content}</p>
      <span className={`text-xs font-medium px-2 py-1 rounded-full ${
        story.status === 'approved' ? 'bg-green-100 text-green-700' :
        story.status === 'denied' ? 'bg-red-100 text-red-700' :
        'bg-yellow-100 text-yellow-700'
      }`}>{story.status}</span>

      {onApprove && onDeny && onDelete && (
        <div className="mt-4 flex gap-2">
          <button onClick={() => onApprove(story.id)} className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 text-sm">Approve</button>
          <button onClick={() => onDeny(story.id)} className="px-3 py-1 bg-red-400 text-white rounded hover:bg-red-500 text-sm">Deny</button>
          <button onClick={() => onDelete(story.id)} className="px-3 py-1 bg-gray-400 text-white rounded hover:bg-gray-500 text-sm">Delete</button>
        </div>
      )}
    </div>
  );
}
