import { Text, Flex, useDisclosure } from '@chakra-ui/react';
import React from 'react';
import PreciseStarRating from '../PreciseStarRating';
import ReviewViewModal from './ReviewViewModal';

export type ReviewProps = {
  description: string;
  rating: number;
  voucherName?: string;
  authorName?: string;
  isAuthor?: boolean;
  dateCreated: Date;
};

const MAIN_TEXT = 'chowdownGray.800';
const SUB_TEXT = 'chowdownGray.500';

const ReviewCard: React.FC<ReviewProps> = ({
  description,
  rating,
  voucherName,
  dateCreated,
  authorName,
  isAuthor
}) => {
  const { isOpen, onClose, onOpen } = useDisclosure();

  return (
    <Flex
      bg="white"
      direction="column"
      w="100%"
      borderRadius="lg"
      borderWidth="2px"
      borderColor="chowdown.lavender"
      boxShadow="md"
      color={MAIN_TEXT}
      py="6"
      px="8"
      gap="2"
      cursor="pointer"
      onClick={onOpen}>
      <Flex justifyContent="space-between" gap="8">
        <Text fontWeight="bold" noOfLines={[2, 2, 1]}>
          {description}
        </Text>
        <PreciseStarRating rating={rating} />
      </Flex>

      <Flex
        justifyContent="space-between"
        flexWrap={{ base: 'wrap', md: 'nowrap' }}>
        <Text fontSize="sm" as="i" color={SUB_TEXT}>
          Voucher:{' '}
          <Text as="span" fontWeight="semibold">
            {voucherName}
          </Text>
        </Text>

        <Text
          fontSize="sm"
          as="i"
          color={SUB_TEXT}
          minWidth={{ md: 'max-content' }}>
          Review left by{' '}
          <Text as="span" fontWeight="semibold">
            {isAuthor ? 'you' : authorName ?? 'an Anonymous User'}
          </Text>{' '}
          on{' '}
          <Text as="span" fontWeight="semibold">
            {dateCreated.toLocaleDateString()}
          </Text>{' '}
        </Text>
      </Flex>

      <ReviewViewModal
        isOpen={isOpen}
        onClose={onClose}
        dateCreated={dateCreated}
        description={description}
        rating={rating}
        authorName={authorName}
        isAuthor={isAuthor}
        voucherName={voucherName}
      />
    </Flex>
  );
};

export default ReviewCard;
