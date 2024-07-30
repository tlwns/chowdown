import { ModalProps } from '@chakra-ui/react';

export type ModalSkeletonProps = {
  title: string;
  body: React.ReactNode;
  size?: ModalProps['size'];
  onClose: ModalProps['onClose'];
  isOpen: ModalProps['isOpen'];
};

export type CommonFormProps = {
  onSubmitSuccess: (res: AuthenticationResponse) => void;
  onSubmitError: (err: unknown) => void;
};

export type CommonModalProps = CommonFormProps & {
  isOpen: ModalSkeletonProps['isOpen'];
  onClose: ModalSkeletonProps['onClose'];
};
