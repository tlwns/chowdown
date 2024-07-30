import { StarIcon } from '@chakra-ui/icons';
import { Flex, Box, useToken } from '@chakra-ui/react';
import React from 'react';

type PreciseStarRatingProps = {
  rating: number;
  noRating?: boolean;
};

const PreciseStarRating: React.FC<PreciseStarRatingProps> = ({
  rating,
  noRating
}) => {
  const space1 = useToken('spacing', 'space.1');

  if (noRating) {
    return (
      <Box position="relative" w="136px">
        <Flex gap={space1}>
          <StarIcon h="6" w="6" color="gray.200" />
          <StarIcon h="6" w="6" color="gray.200" />
          <StarIcon h="6" w="6" color="gray.200" />
          <StarIcon h="6" w="6" color="gray.200" />
          <StarIcon h="6" w="6" color="gray.200" />
        </Flex>
      </Box>
    );
  }

  return (
    <Box position="relative" w="136px" title={`Rating: ${rating.toFixed(2)}`}>
      <Flex gap={space1}>
        <StarIcon h="6" w="6" color="gray.100" />
        <StarIcon h="6" w="6" color="gray.100" />
        <StarIcon h="6" w="6" color="gray.100" />
        <StarIcon h="6" w="6" color="gray.100" />
        <StarIcon h="6" w="6" color="gray.100" />
      </Flex>
      <Flex
        gap={space1}
        position="absolute"
        top="0"
        // scale size out of 100% subtracting the gaps, add back the gaps
        width={
          rating === 5
            ? '100%'
            : `calc((${rating / 5} * (100% - (4 * ${space1}))) + (${space1} * ${Math.floor(rating)}))`
        }
        overflow="hidden">
        <StarIcon h="6" w="6" color="yellow.400" />
        <StarIcon h="6" w="6" color="yellow.400" />
        <StarIcon h="6" w="6" color="yellow.400" />
        <StarIcon h="6" w="6" color="yellow.400" />
        <StarIcon h="6" w="6" color="yellow.400" />
      </Flex>
    </Box>
  );
};

export default PreciseStarRating;
