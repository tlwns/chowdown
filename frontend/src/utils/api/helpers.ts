import { AxiosRequestConfig } from 'axios';

export const withAuthHeaders = (
  token: string
): AxiosRequestConfig['headers'] => {
  return {
    Authorization: `Bearer ${token}`
  };
};
