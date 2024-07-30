import React from 'react';
import ModalSkeleton from './ModalSkeleton';
import { Link, Text } from '@chakra-ui/react';
import { CommonModalProps } from './types';
import CustomerRegistrationForm from './forms/CustomerRegistrationForm';

type CustomerRegistrationModalProps = CommonModalProps & {
  onNewEatery: () => void;
  onExistingCustomer: () => void;
};

const CustomerRegistrationModal: React.FC<CustomerRegistrationModalProps> = ({
  onSubmitError,
  onSubmitSuccess,
  isOpen,
  onClose,
  onNewEatery,
  onExistingCustomer
}) => {
  return (
    <ModalSkeleton
      title="Customer Registration"
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      body={
        <>
          <CustomerRegistrationForm
            onSubmitError={onSubmitError}
            onSubmitSuccess={onSubmitSuccess}
          />
          <Link
            color="chowdown.lavender"
            textAlign="center"
            onClick={onNewEatery}>
            Trying to register as an eatery?
          </Link>
          <Text textAlign="center">
            Already a customer?{' '}
            <Link color="chowdown.lavender" onClick={onExistingCustomer}>
              Login Here
            </Link>
          </Text>
        </>
      }
    />
  );
};

export default CustomerRegistrationModal;
