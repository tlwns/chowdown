import { Box } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';

import EateryAlbum from '../components/EateryAlbum';
import { EateryBrief } from '../types/eateryTypes';
import LoadingPage from './LoadingPage';
import { getEateryList } from '../utils/api/eateries';

const UserHomePage = () => {
  const {
    data: eateries,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eateries'],
    queryFn: getEateryList,
    select: (data) => {
      return data.eateries.map(
        (eatery) =>
          ({
            eateryId: eatery.eatery_id,
            eateryName: eatery.eatery_name,
            numVouchers: eatery.num_vouchers,
            topThreeVouchers: eatery.top_three_vouchers,
            thumbnailURI: eatery.thumbnail_uri,
            averageRating: eatery.average_rating
          }) satisfies EateryBrief
      );
    }
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <Box flex={1} bg="chowdownPurple.50" px={{ base: 4, sm: 12 }} py={8}>
        <EateryAlbum eateries={eateries} />
      </Box>
    )
  );
};

export default UserHomePage;
