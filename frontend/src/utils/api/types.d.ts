//
// Common
//
type UserType = 'eatery' | 'customer';
type SessionToken = string;

type FullAddress = {
  country: string;
  state: string;
  county: string;
  city: string;
  street: string;
  postcode: string;
  house_number: string;
  unit_number: string;
  longitude: number;
  latitude: number;
  fmt_address: string;
};

//
// Authentication
//
type CustomerLoginRequest = {
  email: string;
  password: string;
};

type CustomerRegistrationRequest = {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  address: FullAddress;
};

type EateryLoginRequest = {
  email: string;
  password: string;
};

type EateryRegistrationRequest = {
  email: string;
  password: string;
  business_name: string;
  manager_first_name: string;
  manager_last_name: string;
  address: FullAddress;
  phone_number: string;
  abn: string;
};

type AuthenticationResponse = {
  access_token: SessionToken;
  user_id: number;
  user_type: UserType;
};

//
// Eatery Management
//
type EateryListResponse = {
  eateries: {
    eatery_id: number;
    eatery_name: string;
    thumbnail_uri: string;
    num_vouchers: number;
    top_three_vouchers: [number, string][];
    average_rating: number;
  }[];
};

type EateryDetailsResponse = {
  name: string;
  email: string;
  description: string;
  phone_number: string;
  address: { unit_number: string; formatted_str: string };
  manager_first_name: string;
  manager_last_name: string;
  abn: string;
  thumbnail_uri: string;
  menu_uri?: string;
  keywords: string[];
  date_joined: Date;
  average_rating: number;
};

type EateryUpdateDetailsRequest = {
  name?: string;
  email?: string;
  description?: string;
  phone_number?: string;
  address?: FullAddress;
  manager_first_name?: string;
  manager_last_name?: string;
  keywords?: string[];
  password?: string;
};

type EateryUpdateThumbnailRequest = {
  thumbnail_uri: string;
};

type EateryUpdateMenuRequest = {
  menu_uri: string;
};

type EateryPublicDetailsResponse = {
  name: string;
  description: string;
  phone_number: string;
  address: { unit_number: string; formatted_str: string };
  thumbnail_uri: string;
  menu_uri?: string;
  keywords: string[];
  average_rating: number;
};

type EateryVouchersResponse = {
  vouchers: {
    voucher_id: number;
    name: string;
    description: string;
    conditions: string;
    total_quantity: number;
    unclaimed_quantity: number;
    expiry: Date;
  }[];
};

type EateryAddReviewRequest = {
  voucher_instance_id: number;
  description: string;
  rating: number;
  anonymous: boolean;
};

type EateryReviewsResponse = {
  reviews: {
    review_id: number;
    description: string;
    rating: number;
    date_created: Date;
    voucher_id: number;
    voucher_name: string;
    voucher_instance_id: number;
    author_id?: number;
    author_name?: string;
  }[];
};

//
// Voucher management
//

type VoucherResponse = {
  voucher_id: number;
  name: string;
  description: string;
  conditions: string;
  total_quantity: number;
  unclaimed_quantity: number;
  expiry: Date;
};

type VoucherCreationRequest = {
  eatery_id: number;
  name: string;
  description: string;
  conditions: string;
  quantity: number;
  release: string; // date time string
  duration: string; // timedelta string
  schedule?: 'daily' | 'weekly' | 'fortnightly' | 'monthly';
};

type VoucherCreationResponse = {
  voucher_template_id: number;
};

type VoucherStatusType =
  | 'unpublished'
  | 'unclaimed'
  | 'claimed'
  | 'redeemed'
  | 'reserved';
type VoucherClaimRequest = {
  customer_id: number;
};

type VoucherClaimResponse = {
  voucher_instance_id: number;
};

type VoucherRedeemResponse = {
  redemption_code: string;
};

type VoucherRedemptionDetailsResponse = {
  eatery_id: number;
  name: string;
  description: string;
  conditions: string;
  expiry: Date;
};

//
// Customer management
//
type CustomerProfileResponse = {
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  address: { unit_number: string; formatted_str: string };
};

type CustomerProfileUpdateRequest = {
  email?: string;
  password?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  address?: FullAddress;
};

type CustomerVouchersResponse = {
  vouchers: {
    voucher_id: number;
    voucher_instance_id: number;
    eatery_id: number;
    name: string;
    description: string;
    conditions: string;
    status: VoucherStatusType;
    expiry: Date;
    review_id?: number;
    given_rating?: number;
  }[];
};

//
// Other API resources
//
type GeoDataResponse = {
  name?: string;
  country: string;
  state: string;
  city?: string;
  county?: string;
  lon: number;
  lat: number;
  street?: string;
  postcode?: string;
  house_no?: string;
  formatted: string;
  [_other: string]: unknown;
};

type AddressCompletionResponse = {
  results: GeoDataResponse[];
  // query: object;
};
