import axios from 'axios';
import { z } from 'zod';
import { withAuthHeaders } from './helpers';

const customerProfileSchema = z.strictObject({
  email: z.string().email(),
  first_name: z.string(),
  last_name: z.string(),
  phone_number: z.string(),
  address: z.strictObject({
    unit_number: z.string(),
    formatted_str: z.string()
  })
});

const customerVouchersSchema = z.strictObject({
  vouchers: z
    .strictObject({
      voucher_instance_id: z.number().int(),
      voucher_id: z.number().int(),
      eatery_id: z.number().int(),
      name: z.string(),
      description: z.string(),
      conditions: z.string(),
      status: z.enum([
        'unpublished',
        'unclaimed',
        'claimed',
        'redeemed',
        'reserved'
      ]),
      expiry: z
        .string()
        .datetime()
        .transform((d) => new Date(d)),
      review_id: z
        .number()
        .int()
        .nullish()
        .transform((v) => v ?? undefined),
      given_rating: z
        .number()
        .min(0)
        .max(5)
        .default(3)
        .nullish()
        .transform((v) => v ?? undefined)
    })
    .array()
});

export const getCustomerProfile = async (
  token: string,
  customerId: number
): Promise<CustomerProfileResponse> => {
  const res = await axios.get<CustomerProfileResponse>(
    `/customer/${customerId}/profile`,
    {
      headers: withAuthHeaders(token)
    }
  );

  return customerProfileSchema.parse(res.data);
};

export const updateCustomerProfile = async (
  token: string,
  customerId: number,
  data: CustomerProfileUpdateRequest
): Promise<void> => {
  await axios.put<void>(`/customer/${customerId}/profile`, data, {
    headers: withAuthHeaders(token)
  });
};

export const getCustomerVouchers = async (
  token: string,
  customerId: number
): Promise<CustomerVouchersResponse> => {
  const res = await axios.get<CustomerVouchersResponse>(
    `/customer/${customerId}/vouchers`,
    {
      headers: withAuthHeaders(token)
    }
  );

  return customerVouchersSchema.parse(res.data);
};
