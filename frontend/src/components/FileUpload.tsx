import React, { useState } from 'react';
import styled from 'styled-components';

interface FileUploadProps {
  onFilesSelected: (files: FileList) => void;
}

const UploadContainer = styled.div`
  padding: 1rem;
  max-width: 500px;
  border: 2px dashed #646cff;
  border-radius: 8px;
  text-align: center;
  margin: 1rem 0;
  margin: 0 auto;
  width: 100%;
  
  &:hover {
    background-color: rgba(100, 108, 255, 0.1);
  }
`;

const FileList = styled.ul`
  list-style: none;
  padding: 0;
  margin-top: 1rem;
`;

const FileItem = styled.li`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  margin: 0.5rem 0;
  border-radius: 4px;
`;

const FileUpload: React.FC<FileUploadProps> = ({ onFilesSelected }) => {
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length <= 10) {
      setSelectedFiles(files);
      onFilesSelected(files);
    } else {
      alert('You can upload a maximum of 10 PDF files.');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length <= 10) {
      setSelectedFiles(files);
      onFilesSelected(files);
    } else {
      alert('You can upload a maximum of 10 PDF files.');
    }
  };

  return (
    <UploadContainer
      onDragOver={handleDragOver}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      style={{ background: isDragging ? 'rgba(100, 108, 255, 0.2)' : 'transparent' }}
    >
      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf"
        multiple
        style={{ display: 'none' }}
        id="file-upload"
      />
      <label htmlFor="file-upload">
        Drop PDF files here or click to upload
      </label>
      {selectedFiles && (
        <FileList>
          {Array.from(selectedFiles).map((file, index) => (
            <FileItem key={index}>
              {file.name}
            </FileItem>
          ))}
        </FileList>
      )}
    </UploadContainer>
  );
};

export default FileUpload;