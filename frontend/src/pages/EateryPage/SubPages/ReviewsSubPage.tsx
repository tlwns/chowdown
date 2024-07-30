import { useQuery } from '@tanstack/react-query';
import { getEateryReviews } from '../../../utils/api/eateries';
import { useParams } from 'react-router-dom';
import LoadingPage from '../../LoadingPage';
import { Flex, VStack, Text } from '@chakra-ui/react';
import { useContext } from 'react';
import { AuthContext } from '../../../context/authContext';
import ReviewCard from '../../../components/Reviews/ReviewCard';

const ReviewsSubPage = () => {
  const { eateryId } = useParams();
  const {
    getters: { userId }
  } = useContext(AuthContext);

  const { data, isLoading, isSuccess } = useQuery({
    queryKey: ['eatery', parseInt(eateryId!), 'reviews'],
    queryFn: () => getEateryReviews(parseInt(eateryId!))
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <VStack w="100%" h="100%" gap="4">
        {data.reviews.length !== 0 ? (
          <>
            {data.reviews.map((review) => {
              return (
                <ReviewCard
                  key={review.review_id}
                  description={review.description}
                  rating={review.rating}
                  voucherName={review.voucher_name}
                  authorName={review.author_name}
                  isAuthor={!!userId && userId === review.author_id}
                  dateCreated={review.date_created}
                />
              );
            })}
          </>
        ) : (
          <Flex
            width={'100%'}
            boxShadow={'md'}
            bg="white"
            borderRadius="lg"
            justify="center"
            px={8}
            py={6}>
            <Text fontSize="lg">Sorry! No reviews yet 😔</Text>
          </Flex>
        )}
      </VStack>
    )
  );
};

export default ReviewsSubPage;
