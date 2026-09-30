import axios from 'axios';

const API = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export async function createProject(name: string, description?: string) {
  const { data } = await API.post('/projects/', { name, description });
  return data;
}

export async function getProjects() {
  const { data } = await API.get('/projects/');
  return data;
}

export async function analyzeCode(projectId: string, code: string) {
  const { data } = await API.post('/analyze/', { project_id: projectId, code });
  return data;
}
