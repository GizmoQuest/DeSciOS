import React, { useEffect, useState } from 'react';
import CreateCollaboration from './CreateCollaboration';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const EditCollaboration = () => {
  const { id } = useParams();
  const { api } = useAuth();
  const [workspace, setWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get(`/collaboration/${id}`);
        setWorkspace(res.data.collaboration);
      } catch {
        setError('Failed to load workspace');
      } finally {
        setLoading(false);
      }
    })();
  }, [api, id]);

  if (loading) return null;
  if (error) return <div>{error}</div>;

  return <CreateCollaboration editing initialData={workspace} />;
};

export default EditCollaboration; 