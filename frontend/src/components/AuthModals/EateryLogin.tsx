import React from 'react';
import ModalSkeleton from './ModalSkeleton';
import { Link, Text } from '@chakra-ui/react';
import { CommonModalProps } from './types';
import EateryLoginForm from './forms/EateryLoginForm';

type EateryLoginModalProps = CommonModalProps & {
  onExistingCustomer: () => void;
  onNewEatery: () => void;
};

const EateryLoginModal: React.FC<EateryLoginModalProps> = ({
  onSubmitError,
  onSubmitSuccess,
  isOpen,
  onClose,
  onExistingCustomer,
  onNewEatery
}) => {
  return (
    <ModalSkeleton
      title="Eatery Login"
      isOpen={isOpen}
      onClose={onClose}
      body={
        <>
          <EateryLoginForm
            onSubmitError={onSubmitError}
            onSubmitSuccess={onSubmitSuccess}
          />
          <Link
            color="chowdown.lavender"
            textAlign="center"
            onClick={onExistingCustomer}>
            Trying to login as a customer?
          </Link>
          <Text textAlign="center">
            New eatery?{' '}
            <Link color="chowdown.lavender" onClick={onNewEatery}>
              Register Here
            </Link>
          </Text>
        </>
      }
    />
  );
};

export default EateryLoginModal;
