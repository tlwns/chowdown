import { Box, Heading } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { EateryBrief } from '../../types/eateryTypes';
import EateryAlbum from '../../components/EateryAlbum';
import LoadingPage from '../LoadingPage';
import {
  getEateryList,
  getPersonalisedEateryList
} from '../../utils/api/eateries';
import { useContext } from 'react';
import { AuthContext } from '../../context/authContext';

const CustomerHomePage = () => {
  const {
    getters: { sessionToken }
  } = useContext(AuthContext);

  const {
    data: eateries,
    isLoading: isLoadingAll,
    isSuccess: isSuccessAll
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

  const {
    data: discover_eateries,
    isLoading: isLoadingDiscover,
    isSuccess: isSuccessDiscover
  } = useQuery({
    queryKey: ['personalised', 'discover'],
    queryFn: () =>
      getPersonalisedEateryList(
        sessionToken!,
        ['rating', 'not_tried', 'distance', 'newest'],
        10
      ),
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

  const {
    data: popular_eateries,
    isLoading: isLoadingPopular,
    isSuccess: isSuccessPopular
  } = useQuery({
    queryKey: ['personalised', 'popular'],
    queryFn: () =>
      getPersonalisedEateryList(
        sessionToken!,
        ['rating', 'vouchers', 'distance'],
        10
      ),
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

  if (isLoadingAll || isLoadingDiscover || isLoadingPopular) {
    return <LoadingPage />;
  }

  return (
    <Box flex={1} bg="chowdownPurple.50" px={{ base: 4, sm: 12 }} py={8}>
      {isSuccessDiscover && (
        <>
          {discover_eateries.length > 0 && (
            <Heading size="lg" pt={10} pb={6}>
              Try something new
            </Heading>
          )}
          <EateryAlbum eateries={discover_eateries} />
        </>
      )}

      {isSuccessPopular && (
        <>
          {popular_eateries.length > 0 && (
            <Heading size="lg" pt={10} pb={6}>
              Most popular local eateries
            </Heading>
          )}
          <EateryAlbum eateries={popular_eateries} />
        </>
      )}

      <Heading size="lg" pt={10} pb={6}>
        All Eateries
      </Heading>
      {isSuccessAll && <EateryAlbum eateries={eateries} />}
    </Box>
  );
};

export default CustomerHomePage;
