import { useSearchParams } from 'react-router-dom';
import { Box, Flex, Text } from '@chakra-ui/react';
import EateryAlbum from '../components/EateryAlbum';
import LoadingPage from './LoadingPage';
import { useQuery } from '@tanstack/react-query';
import { getSearchResults } from '../utils/api/eateries';
import { EateryBrief } from '../types/eateryTypes';
const SearchPage = () => {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('search_query');

  const {
    data: eateries,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eateries', searchQuery],
    queryFn: () => getSearchResults(searchQuery!),
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

  return isSuccess ? (
    eateries.length !== 0 ? (
      <Box flex={1} bg="chowdownPurple.50" px={{ base: 4, sm: 12 }} py={8}>
        <EateryAlbum eateries={eateries} />
      </Box>
    ) : (
      <Box flex={1} bg="chowdownPurple.50" px={{ base: 4, sm: 12 }} py={8}>
        <Flex
          width={'100%'}
          boxShadow={'md'}
          bg="white"
          borderRadius="lg"
          justify="center"
          px={8}
          py={6}>
          <Text fontSize="lg">Sorry! No matching eateries found 😔</Text>
        </Flex>
      </Box>
    )
  ) : null;
};

export default SearchPage;
