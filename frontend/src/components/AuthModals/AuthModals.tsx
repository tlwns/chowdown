import React from 'react';
import { AuthModalControls } from './useAuthModalControls';
import CustomerRegistrationModal from './CustomerRegistration';
import { CommonFormProps } from './types';
import CustomerLoginModal from './CustomerLogin';
import EateryLoginModal from './EateryLogin';
import EateryRegistrationModal from './EateryRegistration';

type AuthModalsProps = CommonFormProps & {
  controls: AuthModalControls;
};

const AuthModals: React.FC<AuthModalsProps> = ({
  controls: cs,
  onSubmitError,
  onSubmitSuccess
}) => {
  return (
    <>
      <CustomerRegistrationModal
        isOpen={cs.current === 'customerRegistration'}
        onClose={cs.setClosed}
        onExistingCustomer={cs.setCustomerLogin}
        onNewEatery={cs.setEateryRegistration}
        onSubmitError={onSubmitError}
        onSubmitSuccess={onSubmitSuccess}
      />
      <CustomerLoginModal
        isOpen={cs.current === 'customerLogin'}
        onClose={cs.setClosed}
        onExistingEatery={cs.setEateryLogin}
        onNewCustomer={cs.setCustomerRegistration}
        onSubmitError={onSubmitError}
        onSubmitSuccess={onSubmitSuccess}
      />
      <EateryLoginModal
        isOpen={cs.current === 'eateryLogin'}
        onClose={cs.setClosed}
        onExistingCustomer={cs.setCustomerLogin}
        onNewEatery={cs.setEateryRegistration}
        onSubmitError={onSubmitError}
        onSubmitSuccess={onSubmitSuccess}
      />
      <EateryRegistrationModal
        isOpen={cs.current === 'eateryRegistration'}
        onClose={cs.setClosed}
        onExistingEatery={cs.setEateryLogin}
        onNewCustomer={cs.setCustomerRegistration}
        onSubmitError={onSubmitError}
        onSubmitSuccess={onSubmitSuccess}
      />
    </>
  );
};

export default AuthModals;
