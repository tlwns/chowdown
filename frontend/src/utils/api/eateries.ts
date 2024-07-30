import axios from 'axios';
import { z } from 'zod';
import { withAuthHeaders } from './helpers';

const idSchema = z.number().int();

const eateryListSchema = z.strictObject({
  eateries: z
    .strictObject({
      eatery_id: idSchema,
      eatery_name: z.string(),
      thumbnail_uri: z.string(),
      num_vouchers: z.number().int().nonnegative(),
      top_three_vouchers: z.tuple([idSchema, z.string()]).array(),
      average_rating: z.number().min(0).max(5)
    })
    .array()
});

const eateryDetailsSchema = z.strictObject({
  name: z.string(),
  email: z.string().email(),
  description: z.string(),
  phone_number: z.string(),
  address: z.strictObject({
    unit_number: z.string(),
    formatted_str: z.string()
  }),
  manager_first_name: z.string(),
  manager_last_name: z.string(),
  abn: z.string(),
  thumbnail_uri: z.string(),
  menu_uri: z
    .string()
    .nullish()
    .transform((v) => v ?? undefined),
  keywords: z.string().array(),
  date_joined: z
    .string()
    .datetime()
    .transform((d) => new Date(d)),
  average_rating: z.number().min(0).max(5)
});

const eateryPublicDetailsSchema = z.strictObject({
  name: z.string(),
  description: z.string(),
  phone_number: z.string(),
  address: z.strictObject({
    unit_number: z.string(),
    formatted_str: z.string()
  }),
  thumbnail_uri: z.string(),
  menu_uri: z
    .string()
    .nullish()
    .transform((v) => v ?? undefined),
  keywords: z.string().array(),
  average_rating: z.number().min(0).max(5)
});

const eateryVouchersSchema = z.strictObject({
  vouchers: z
    .strictObject({
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
    })
    .array()
});

const eateryReviewsSchema = z.strictObject({
  reviews: z
    .strictObject({
      review_id: z.number().int(),
      description: z.string(),
      rating: z.number().min(0).max(5),
      date_created: z
        .string()
        .datetime()
        .transform((d) => new Date(d)),
      voucher_id: z.number().int(),
      voucher_name: z.string(),
      voucher_instance_id: z.number().int(),
      author_id: z
        .number()
        .int()
        .nullish()
        .transform((v) => v ?? undefined),
      author_name: z
        .string()
        .nullish()
        .transform((v) => v ?? undefined)
    })
    .array()
});

export const getEateryList = async (): Promise<EateryListResponse> => {
  const res = await axios.get<EateryListResponse>('/eatery/list');

  return eateryListSchema.parse(res.data);
};

export const getEateryDetails = async (
  token: string,
  eateryId: number
): Promise<EateryDetailsResponse> => {
  const res = await axios.get<EateryDetailsResponse>(
    `/eatery/${eateryId}/details`,
    {
      headers: withAuthHeaders(token)
    }
  );

  return eateryDetailsSchema.parse(res.data);
};

export const updateEateryDetails = async (
  token: string,
  eateryId: number,
  data: EateryUpdateDetailsRequest
): Promise<void> => {
  await axios.put<void>(`/eatery/${eateryId}/details`, data, {
    headers: withAuthHeaders(token)
  });
};

export const updateEateryThumbnail = async (
  token: string,
  eateryId: number,
  thumbnailURI: string
): Promise<void> => {
  await axios.put<void>(
    `/eatery/${eateryId}/thumbnail`,
    {
      thumbnail_uri: thumbnailURI
    } satisfies EateryUpdateThumbnailRequest,
    {
      headers: withAuthHeaders(token)
    }
  );
};

export const updateEateryMenu = async (
  token: string,
  eateryId: number,
  menuURI: string
): Promise<void> => {
  await axios.put<void>(
    `/eatery/${eateryId}/menu`,
    {
      menu_uri: menuURI
    } satisfies EateryUpdateMenuRequest,
    {
      headers: withAuthHeaders(token)
    }
  );
};

export const getEateryPublicDetails = async (
  eateryId: number
): Promise<EateryPublicDetailsResponse> => {
  const res = await axios.get<EateryPublicDetailsResponse>(
    `/eatery/${eateryId}/details/public`
  );

  return eateryPublicDetailsSchema.parse(res.data);
};

export const getEateryVouchers = async (
  eateryId: number
): Promise<EateryVouchersResponse> => {
  const res = await axios.get<EateryVouchersResponse>(
    `/eatery/${eateryId}/vouchers`
  );

  return eateryVouchersSchema.parse(res.data);
};

export const getSearchResults = async (
  searchQuery: string
): Promise<EateryListResponse> => {
  const res = await axios.get<EateryListResponse>('/eatery/search', {
    params: {
      search_query: searchQuery
    }
  });

  return eateryListSchema.parse(res.data);
};

export const getPersonalisedEateryList = async (
  token: string,
  sortBy: string[],
  maxCount: number
): Promise<EateryListResponse> => {
  const res = await axios.get<EateryListResponse>('/eatery/list/personalised', {
    params: {
      sort_by: sortBy,
      max_count: maxCount
    },
    paramsSerializer: {
      indexes: null
    },
    headers: withAuthHeaders(token)
  });

  return eateryListSchema.parse(res.data);
};

export const addEateryReview = async (
  customerToken: string,
  eateryId: number,
  data: EateryAddReviewRequest
): Promise<void> => {
  // NOTE: actually returns a review_id response
  await axios.post(`/eatery/${eateryId}/reviews`, data, {
    headers: withAuthHeaders(customerToken)
  });
};

export const getEateryReviews = async (
  eateryId: number
): Promise<EateryReviewsResponse> => {
  const res = await axios.get(`/eatery/${eateryId}/reviews`);

  return eateryReviewsSchema.parse(res.data);
};
