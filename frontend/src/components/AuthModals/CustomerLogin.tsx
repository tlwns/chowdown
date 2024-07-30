import React from 'react';
import ModalSkeleton from './ModalSkeleton';
import { Link, Text } from '@chakra-ui/react';
import { CommonModalProps } from './types';
import CustomerLoginForm from './forms/CustomerLoginForm';

type CustomerLoginModalProps = CommonModalProps & {
  onExistingEatery: () => void;
  onNewCustomer: () => void;
};

const CustomerLoginModal: React.FC<CustomerLoginModalProps> = ({
  onSubmitError,
  onSubmitSuccess,
  isOpen,
  onClose,
  onExistingEatery,
  onNewCustomer
}) => {
  return (
    <ModalSkeleton
      title="Customer Login"
      isOpen={isOpen}
      onClose={onClose}
      body={
        <>
          <CustomerLoginForm
            onSubmitError={onSubmitError}
            onSubmitSuccess={onSubmitSuccess}
          />
          <Link
            color="chowdown.lavender"
            textAlign="center"
            onClick={onExistingEatery}>
            Trying to login as an eatery?
          </Link>
          <Text textAlign="center">
            New customer?{' '}
            <Link color="chowdown.lavender" onClick={onNewCustomer}>
              Register Here
            </Link>
          </Text>
        </>
      }
    />
  );
};

export default CustomerLoginModal;
