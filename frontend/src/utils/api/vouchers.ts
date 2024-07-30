import axios from 'axios';
import { z } from 'zod';
import { withAuthHeaders } from './helpers';

const voucherResponseSchema = z.strictObject({
  voucher_id: z.number().int(),
  name: z.string(),
  description: z.string(),
  conditions: z.string(),
  total_quantity: z.number().int().nonnegative(),
  unclaimed_quantity: z.number().int().nonnegative(),
  expiry: z
    .string()
    .datetime()
    .transform((d) => new Date(d))
});

const voucherCreationResponseSchema = z.strictObject({
  voucher_template_id: z.number().int()
});

const voucherClaimResponseSchema = z.strictObject({
  voucher_instance_id: z.number().int()
});

const voucherRedeemResponseSchema = z.strictObject({
  redemption_code: z.string()
});

const redeemedVoucherDetailsResponseSchema = z.strictObject({
  eatery_id: z.number().int(),
  name: z.string(),
  description: z.string(),
  conditions: z.string(),
  expiry: z
    .string()
    .datetime()
    .transform((d) => new Date(d))
});

export const getVoucher = async (
  voucherId: string
): Promise<VoucherResponse> => {
  const res = await axios.get<VoucherResponse>(`/voucher/${voucherId}`);

  return voucherResponseSchema.parse(res.data);
};

export const createVoucher = async (
  token: string,
  data: VoucherCreationRequest
): Promise<VoucherCreationResponse> => {
  const res = await axios.post<VoucherCreationResponse>('/voucher', data, {
    headers: withAuthHeaders(token)
  });

  return voucherCreationResponseSchema.parse(res.data);
};

export const claimVoucher = async (
  token: string,
  voucherId: number,
  data: VoucherClaimRequest
): Promise<VoucherClaimResponse> => {
  const res = await axios.put<VoucherClaimResponse>(
    `/voucher/claim/${voucherId}`,
    data,
    {
      headers: withAuthHeaders(token)
    }
  );

  return voucherClaimResponseSchema.parse(res.data);
};

export const redeemVoucher = async (
  token: string,
  voucherInstanceId: number
): Promise<VoucherRedeemResponse> => {
  const res = await axios.put<void>(
    `/voucher/instance/${voucherInstanceId}/redeem`,
    {},
    {
      headers: withAuthHeaders(token)
    }
  );

  return voucherRedeemResponseSchema.parse(res.data);
};

export const getRedeemedVoucherDetails = async (
  token: string,
  redemption_code: string
): Promise<VoucherRedemptionDetailsResponse> => {
  const res = await axios.get<VoucherRedemptionDetailsResponse>(
    `/voucher/redemption/${redemption_code}`,
    {
      headers: withAuthHeaders(token)
    }
  );

  return redeemedVoucherDetailsResponseSchema.parse(res.data);
};

export const acceptRedeemedVoucher = async (
  token: string,
  redemption_code: string
): Promise<void> => {
  await axios.put<VoucherRedemptionDetailsResponse>(
    `/voucher/redemption/${redemption_code}/accept`,
    {},
    {
      headers: withAuthHeaders(token)
    }
  );
};
