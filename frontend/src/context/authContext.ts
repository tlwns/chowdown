import { createContext } from 'react';

export type SessionInfo = {
  sessionToken: SessionToken;
  userId: number;
  userType: UserType;
};

type Getters = {
  sessionToken: SessionToken | undefined;
  userId: number | undefined;
  userType: UserType | undefined;
};

type Setters = {
  setSessionInfo: (info: SessionInfo | undefined) => void;
};

type ContextType = {
  getters: Getters;
  setters: Setters;
};

const initialState: Getters = {
  sessionToken: undefined,
  userId: undefined,
  userType: undefined
};

const AuthContext = createContext<ContextType>({} as ContextType);

export { initialState, AuthContext };
