interface ModalProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmClass?: string; // 👈 Adicionado
  cancelClass?: string;  // 👈 Adicionado
}

export default function Modal({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
  confirmClass = "bg-blue-600 text-white hover:bg-blue-700",
  cancelClass = "bg-gray-300 text-gray-800 hover:bg-gray-400",
}: ModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
        <h2 className="text-lg font-semibold mb-2">{title}</h2>
        <p className="text-sm text-gray-600 mb-4">{message}</p>

        <div className="flex justify-end space-x-2">
          <button
            onClick={onConfirm}
            className={`px-4 py-2 rounded ${confirmClass}`}
          >
            {confirmLabel}
          </button>
          <button
            onClick={onCancel}
            className={`px-4 py-2 rounded ${cancelClass}`}
          >
            {cancelLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
