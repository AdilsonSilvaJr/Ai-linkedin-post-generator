import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import styled from 'styled-components';
import PostPreview from './PostPreview';

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 1rem 0;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 600px;
  margin: 0 auto;
  width: 100%;
`;

const ErrorMessage = styled.span`
  color: #ff4444;
  font-size: 0.875rem;
`;

const StyledTextArea = styled.textarea`
  width: 100%;
  min-height: 150px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  border-color:rgb(133, 133, 133);
  background-color:rgb(59, 59, 59);
`;

const SubmitButton = styled.button`
  margin: 0 auto;
  padding: 8px 32px;
  border-radius: 8px;
  cursor: pointer;
  border-color:rgb(133, 133, 133);
`;

const PreviewSection = styled.div`
  margin-top: 2rem;
  border-top: 1px solid #444;
  padding-top: 1rem;
  max-height: 600px;
  overflow-y: auto;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;

  // Scrollbar styling
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #2d2d2d;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #666;
    border-radius: 4px;
    
    &:hover {
      background: #888;
    }
  }
`;

const PreviewTitle = styled.h3`
  text-align: center;
  margin-bottom: 2rem;
  color: #fff;
`;

const PostGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  width: 100%;
  padding: 0 1rem;

  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;

const LoadingSpinner = styled.div`
  margin: 20px auto;
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

interface PostFormProps {
  onSubmit: (numPosts: number, customPrompt: string) => Promise<void>;
}

interface FormInputs {
  numPosts: number;
  customPrompt: string;
}

const PostForm: React.FC<PostFormProps> = ({ onSubmit }) => {
  const [generatedPosts, setGeneratedPosts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormInputs>();

  const onSubmitForm = async (data: FormInputs) => {
    setIsLoading(true);
    try {
      await onSubmit(Number(data.numPosts), data.customPrompt);
      // Note: You'll need to modify your onSubmit handler to update the generatedPosts state
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Form onSubmit={handleSubmit(onSubmitForm)}>
        <FormGroup>
          <label htmlFor="numPosts">Number of Posts:</label>
          <input
            id="numPosts"
            type="number"
            {...register('numPosts', { 
              required: 'This field is required',
              min: { value: 1, message: 'Minimum value is 1' },
              max: { value: 10, message: 'Maximum value is 10' }
            })}
          />
          {errors.numPosts && <ErrorMessage>{errors.numPosts.message}</ErrorMessage>}
        </FormGroup>
        
        <FormGroup>
          <label htmlFor="customPrompt">Custom Prompt:</label>
          <StyledTextArea
            id="customPrompt"
            {...register('customPrompt', { required: 'This field is required' })}
            rows={4}
          />
          {errors.customPrompt && <ErrorMessage>{errors.customPrompt.message}</ErrorMessage>}
        </FormGroup>

        <SubmitButton type="submit" disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Generate Posts'}
        </SubmitButton>
      </Form>

      {isLoading && <LoadingSpinner />}

      {!isLoading && generatedPosts.length > 0 && (
        <PreviewSection>
          <PreviewTitle>Generated Posts</PreviewTitle>
          <PostGrid>
            {generatedPosts.map((post, index) => (
              <PostPreview key={index} content={post} />
            ))}
          </PostGrid>
        </PreviewSection>
      )}
    </>
  );
};

export default PostForm;