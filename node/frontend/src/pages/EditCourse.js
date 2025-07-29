import React, { useEffect, useState } from 'react';
import CreateCourse from './CreateCourse';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// Re-uses CreateCourse component by passing existing course data and switching to PUT request
const EditCourse = () => {
  const { id } = useParams();
  const { api } = useAuth();
  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const res = await api.get(`/courses/${id}`);
        setInitialData(res.data.course);
      } catch (err) {
        setError('Failed to load course');
      } finally {
        setLoading(false);
      }
    };
    fetchCourse();
  }, [api, id]);

  if (loading) return null; // Could add spinner
  if (error) return <div>{error}</div>;

  return <CreateCourse editing initialData={initialData} />;
};

export default EditCourse; 