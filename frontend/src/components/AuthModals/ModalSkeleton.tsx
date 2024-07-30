import {
  Flex,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay
} from '@chakra-ui/react';
import React from 'react';
import { ModalSkeletonProps } from './types';

const ModalSkeleton: React.FC<ModalSkeletonProps> = ({
  title,
  size,
  body,
  onClose,
  isOpen
}) => {
  return (
    <Modal size={size} isCentered isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent padding="8" mx={{ base: 2, md: 0 }}>
        <ModalHeader textAlign="center">{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Flex gap="4" direction="column">
            {body}
          </Flex>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default ModalSkeleton;
