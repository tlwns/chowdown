import axios from 'axios';
import { z } from 'zod';
import { withAuthHeaders } from './helpers';

const authResponseSchema = z.strictObject({
  access_token: z.string(),
  user_id: z.number().int(),
  user_type: z.enum(['customer', 'eatery'])
});
// .transform((rawRes) => {
//   return {
//     accessToken: rawRes.access_token,
//     userId: rawRes.user_id,
//     userType: rawRes.user_type
//   };
// });

export const refreshTokens = async (): Promise<AuthenticationResponse> => {
  const res = await axios.get<AuthenticationResponse>('/auth/refresh', {
    withCredentials: true
  });

  return authResponseSchema.parse(res.data);
};

export const logout = async (token: string): Promise<void> => {
  await axios.delete('/auth/logout', { headers: withAuthHeaders(token) });
};

export const customerLogin = async (
  email: string,
  password: string
): Promise<AuthenticationResponse> => {
  const res = await axios.post<AuthenticationResponse>(
    '/auth/login/customer',
    {
      email,
      password
    } satisfies CustomerLoginRequest,
    {
      withCredentials: true
    }
  );

  return authResponseSchema.parse(res.data);
};

export const customerRegister = async (
  data: CustomerRegistrationRequest
): Promise<AuthenticationResponse> => {
  const res = await axios.post<AuthenticationResponse>(
    '/auth/register/customer',
    data,
    {
      withCredentials: true
    }
  );

  return authResponseSchema.parse(res.data);
};

export const eateryLogin = async (
  email: string,
  password: string
): Promise<AuthenticationResponse> => {
  const res = await axios.post<AuthenticationResponse>(
    '/auth/login/eatery',
    {
      email,
      password
    } satisfies EateryLoginRequest,
    {
      withCredentials: true
    }
  );

  return authResponseSchema.parse(res.data);
};

export const eateryRegister = async (
  data: EateryRegistrationRequest
): Promise<AuthenticationResponse> => {
  const res = await axios.post<AuthenticationResponse>(
    '/auth/register/eatery',
    data,
    {
      withCredentials: true
    }
  );

  return authResponseSchema.parse(res.data);
};
