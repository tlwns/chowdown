export type EateryPublicDetails = {
  name: string;
  description: string;
  address: string;
  phone_number: string;
  thumbnail_uri: string;
  menu_uri?: string;
  keywords: string[];
};

export type EateryBrief = {
  eateryId: number;
  eateryName: string;
  numVouchers: number;
  topThreeVouchers: [number, string][];
  thumbnailURI: string;
  averageRating: number;
};
