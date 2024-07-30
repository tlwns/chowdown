import { useState } from 'react';

type ModalName =
  | 'customerLogin'
  | 'customerRegistration'
  | 'eateryLogin'
  | 'eateryRegistration';

export type AuthModalControls = {
  current: ModalName | undefined;
  setClosed: () => void;
  setCustomerLogin: () => void;
  setCustomerRegistration: () => void;
  setEateryLogin: () => void;
  setEateryRegistration: () => void;
};

const useAuthModalControls = (startingState?: ModalName): AuthModalControls => {
  const [currentModal, setCurrentModal] = useState<ModalName | undefined>(
    startingState
  );

  return {
    current: currentModal,
    setClosed: () => setCurrentModal(undefined),
    setCustomerLogin: () => setCurrentModal('customerLogin'),
    setCustomerRegistration: () => setCurrentModal('customerRegistration'),
    setEateryLogin: () => setCurrentModal('eateryLogin'),
    setEateryRegistration: () => setCurrentModal('eateryRegistration')
  };
};

export default useAuthModalControls;
