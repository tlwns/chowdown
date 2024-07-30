import {
  AspectRatio,
  Box,
  Card,
  CardBody,
  Flex,
  Heading,
  Image,
  Stack,
  Text
} from '@chakra-ui/react';
import React from 'react';
import { Link } from 'react-router-dom';

import { EateryBrief } from '../types/eateryTypes';
import PreciseStarRating from './PreciseStarRating';

const EateryCard: React.FC<EateryBrief> = ({
  eateryId,
  eateryName,
  numVouchers,
  topThreeVouchers,
  thumbnailURI,
  averageRating
}) => {
  const hasReviews = averageRating !== 0;

  return (
    <>
      <Card
        maxWidth={500}
        overflow="hidden"
        bg="chowdownPurple.50"
        boxShadow="none"
        as={Link}
        to={`/eatery/${eateryId}`}
        fontWeight={'semibold'}>
        <Box pos="relative">
          <AspectRatio ratio={16 / 9}>
            <Image
              src={thumbnailURI}
              alt={`${eateryName}'s thumbnail image`}
              borderRadius="lg"
            />
          </AspectRatio>

          <Stack
            maxW={'40%'}
            position="absolute"
            top={'10%'}
            right={0}
            spacing={4}>
            {topThreeVouchers.map((voucher) => (
              <Text
                flex={1}
                key={voucher[0]}
                fontSize="sm"
                bg="chowdownPink.400"
                opacity={0.8}
                padding={1}
                noOfLines={1}
                borderLeftRadius="lg">
                {voucher[1]}
              </Text>
            ))}
          </Stack>
        </Box>

        <CardBody>
          <Stack spacing={1}>
            <Flex justifyContent="space-between">
              <Heading size="md">{eateryName}</Heading>
              <PreciseStarRating
                rating={averageRating}
                noRating={!hasReviews}
              />
            </Flex>
            <Flex justifyContent="space-between" alignItems="baseline">
              <Text>{numVouchers} vouchers available</Text>
              <Text
                fontSize="sm"
                fontStyle={hasReviews ? 'unset' : 'italic'}
                minWidth="max-content">
                {hasReviews
                  ? `${averageRating.toFixed(1)} stars`
                  : 'No reviews yet'}
              </Text>
            </Flex>
          </Stack>
        </CardBody>
      </Card>
    </>
  );
};

export default EateryCard;
