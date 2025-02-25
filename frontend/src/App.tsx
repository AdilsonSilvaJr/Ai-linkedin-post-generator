import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import FileUpload from './components/FileUpload';
import PostForm from './components/PostForm';
import PostPreview from './components/PostPreview';
import './App.css';

function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [posts, setPosts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFilesSelected = (selectedFiles: FileList) => {
    setFiles(selectedFiles);
  };

  const handleFormSubmit = async (numPosts: number, customPrompt: string) => {
    if (!files) {
      toast.error('Please upload PDF files first.');
      return;
    }

    setIsLoading(true);
    try {
      // Upload files and update vector store
      const formData = new FormData();
      Array.from(files).forEach((file) => formData.append('files', file));

      // First, upload files
      const uploadResponse = await fetch('http://localhost:8000/vector-store/update', {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload files');
      }

      // Then, generate posts with simple JSON data
      const generateResponse = await fetch('http://localhost:8000/generate-posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          num_posts: numPosts,
          custom_prompt: customPrompt
        }),
      });

      if (!generateResponse.ok) {
        throw new Error('Failed to generate posts');
      }

      const data = await generateResponse.json();
      setPosts(data.posts.map((post: { content: string }) => post.content));
      toast.success('Posts generated successfully!');
    } catch (error) {
      console.error('Error:', error);
      toast.error(error instanceof Error ? error.message : 'An error occurred while generating posts');
    } finally {
      setIsLoading(false);
      setProgress(0);
    }
  };

  const handleError = (message: string) => {
    toast.error(message, {
      position: "top-right",
      autoClose: 5000,
      hideProgressBar: false,
    });
  };

  return (
    <div className="App">
      <FileUpload onFilesSelected={handleFilesSelected} />
      <PostForm onSubmit={handleFormSubmit} />
      
      {/* Display the generated posts */}
      {posts.length > 0 && (
        <div>
          <h2>Generated Posts</h2>
          {posts.map((post, index) => (
            <PostPreview key={index} content={post} />
          ))}
        </div>
      )}
      
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </div>
  );
}

export default App;
