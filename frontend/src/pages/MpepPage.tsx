//
// ADD THIS NEW FILE
// File: peptalk/frontend/src/pages/MpepPage.tsx
//
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'; // NEW: Hook to read URL
import ReactMarkdown from 'react-markdown';
import { SelectionPopup } from '../SelectionPopup'; // Import popup

interface MpepPageProps {
  // Function to send a prompt to the AI Panel
  onTriggerAI: (prompt: string, type: 'explain' | 'example' | 'ask') => void;
}

// Define the state for our selection popup
interface PopupState {
  visible: boolean;
  text: string;
  top: number;
  left: number;
}

export function MpepPage({ onTriggerAI }: MpepPageProps) {
  // NEW: Get the 'sectionId' from the URL (e.g., "2141")
  const { sectionId } = useParams<{ sectionId: string }>();
  const [content, setContent] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // State for the text selection popup
  const [popup, setPopup] = useState<PopupState>({
    visible: false,
    text: "",
    top: 0,
    left: 0,
  });

  // This effect re-runs every time the sectionId in the URL changes
  useEffect(() => {
    // Default to 2141 if no section is specified
    const fileId = sectionId || "2141";
    const filename = `mpep_${fileId}.md`;

    setIsLoading(true);
    setError(null);
    setPopup({ ...popup, visible: false }); // Hide popup on page change

    // Fetch the correct MPEP text from the public folder
    fetch(`/${filename}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Could not find file: ${filename}`);
        }
        return response.text();
      })
      .then(text => {
        setContent(text);
        setIsLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch MPEP content:", err);
        setError(`Failed to load content for MPEP ${fileId}.`);
        setIsLoading(false);
      });
  }, [sectionId]); // Dependency array

  const handleMouseUp = (e: React.MouseEvent) => {
    const selection = window.getSelection();
    const selectedText = selection?.toString().trim();

    if (selection && selectedText) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      // We position relative to the *page*, not the viewport
      setPopup({
        visible: true,
        text: selectedText,
        top: e.pageY + 10,
        left: e.pageX + 5,
      });
    } else {
      setPopup({ ...popup, visible: false });
    }
  };

  const hidePopup = () => {
    setPopup({ ...popup, visible: false });
  };

  // --- Popup Button Handlers ---
  const handleExplain = () => {
    onTriggerAI(popup.text, 'explain');
    hidePopup();
  };

  const handleExample = () => {
    onTriggerAI(popup.text, 'example');
    hidePopup();
  };

  const handleAsk = () => {
    onTriggerAI(popup.text, 'ask');
    hidePopup();
  };


  if (isLoading) {
    return <div className="p-8">Loading MPEP content...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">{error}</div>;
  }

  return (
    <div 
      className="p-8 overflow-y-auto h-full" 
      onMouseUp={handleMouseUp}
    >
      <article className="prose lg:prose-xl max-w-none">
        <ReactMarkdown>
          {content}
        </ReactMarkdown>
      </article>

      {/* Render the popup */}
      {popup.visible && (
        <SelectionPopup
          top={popup.top}
          left={popup.left}
          onExplain={handleExplain}
          onExample={handleExample}
          onAsk={handleAsk}
        />
      )}
    </div>
  );
}