import React from 'react';
import ModalSkeleton from './ModalSkeleton';
import EateryRegistrationForm from './forms/EateryRegistrationForm';
import { Link, Text } from '@chakra-ui/react';
import { CommonModalProps } from './types';

type EateryRegistrationModalProps = CommonModalProps & {
  onNewCustomer: () => void;
  onExistingEatery: () => void;
};

const EateryRegistrationModal: React.FC<EateryRegistrationModalProps> = ({
  onSubmitError,
  onSubmitSuccess,
  isOpen,
  onClose,
  onNewCustomer,
  onExistingEatery
}) => {
  return (
    <ModalSkeleton
      title="Eatery Registration"
      size="lg"
      isOpen={isOpen}
      onClose={onClose}
      body={
        <>
          <EateryRegistrationForm
            onSubmitError={onSubmitError}
            onSubmitSuccess={onSubmitSuccess}
          />
          <Link
            color="chowdown.lavender"
            textAlign="center"
            onClick={onNewCustomer}>
            Trying to register as a customer?
          </Link>
          <Text textAlign="center">
            Already an eatery?{' '}
            <Link color="chowdown.lavender" onClick={onExistingEatery}>
              Login Here
            </Link>
          </Text>
        </>
      }
    />
  );
};

export default EateryRegistrationModal;
