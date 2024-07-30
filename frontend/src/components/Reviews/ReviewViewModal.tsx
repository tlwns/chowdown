import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
  Flex,
  ModalFooter,
  Heading
} from '@chakra-ui/react';
import React from 'react';
import { ReviewProps } from './ReviewCard';
import PreciseStarRating from '../PreciseStarRating';

type ReviewViewModalProps = ReviewProps & {
  isOpen: boolean;
  onClose: () => void;
};

const ReviewViewModal: React.FC<ReviewViewModalProps> = ({
  isOpen,
  onClose,
  description,
  rating,
  voucherName,
  dateCreated,
  authorName,
  isAuthor
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent mx={{ base: 2, md: 0 }}>
        <ModalCloseButton />
        <ModalHeader>
          <Heading color="chowdown.gray" fontSize="2xl" fontWeight="bold">
            Review
          </Heading>
        </ModalHeader>
        <ModalBody>
          <Flex direction="column" gap="2">
            <Text>
              <Text as="span" fontWeight="semibold">
                {isAuthor ? 'You' : authorName ?? 'An Anonymous User'}
              </Text>{' '}
              {isAuthor ? 'wrote:' : 'writes:'}{' '}
            </Text>
            <Text as="i">{description}</Text>
            <Flex alignItems="center" gap="1">
              <PreciseStarRating rating={rating} />
              <Text as="i" fontSize="sm" color="gray.500">
                {rating.toFixed(2)}
              </Text>
            </Flex>
          </Flex>
        </ModalBody>
        <ModalFooter>
          <Flex
            w="100%"
            justifyContent="space-between"
            alignItems="flex-end"
            gap="2">
            <Text as="i" fontSize="xs">
              Voucher:{' '}
              <Text as="span" fontWeight="semibold">
                {voucherName}
              </Text>
            </Text>
            <Text
              as="i"
              fontSize="xs"
              display="block"
              textAlign="right"
              minWidth="max-content">
              Reviewed:{' '}
              <Text as="span" fontWeight="semibold">
                {dateCreated.toLocaleDateString()}
              </Text>
            </Text>
          </Flex>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ReviewViewModal;
