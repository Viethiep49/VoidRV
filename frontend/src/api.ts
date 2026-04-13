import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const scrapeRestaurant = async (url: string) => {
  const response = await api.post('/scrape', { url });
  return response.data;
};

export const getJobStatus = async (jobId: string) => {
  const response = await api.get(`/scrape/job/${jobId}`);
  return response.data;
};

export const getRestaurant = async (slug: string) => {
  const response = await api.get(`/restaurants/${slug}`);
  return response.data;
};

export const analyzeRestaurant = async (restaurantId: number) => {
  const response = await api.post(`/analyze/restaurant/${restaurantId}`);
  return response.data;
};
