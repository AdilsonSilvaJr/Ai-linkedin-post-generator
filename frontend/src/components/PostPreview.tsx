import React, { useState } from 'react';
import styled from 'styled-components';

const PreviewCard = styled.div`
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 1rem 0;
  position: relative;
  text-align: left;
`;

const CopyButton = styled.button`
  position: absolute;
  top: 0.3rem;
  right: 0.3rem;
  padding: 2px 12px;
  border-color:rgb(133, 133, 133);
`;

const PostPreview = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 1.5rem;
  border-radius: 8px;
  height: 100%;
  min-height: 200px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

interface PostPreviewProps {
  content: string;
}

const PostPreviewComponent: React.FC<PostPreviewProps> = ({ content }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <PreviewCard>
      <CopyButton onClick={handleCopy}>
        {copied ? 'Copied!' : 'Copy'}
      </CopyButton>
      <p>{content}</p>
    </PreviewCard>
  );
};

export default PostPreviewComponent;