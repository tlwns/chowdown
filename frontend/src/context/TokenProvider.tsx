import React, {
  PropsWithChildren,
  useCallback,
  useEffect,
  useState
} from 'react';

import { AuthContext, initialState } from './authContext';
import type { SessionInfo } from './authContext';
import { Fade, Flex, useBoolean } from '@chakra-ui/react';
import LoadingPage from '../pages/LoadingPage';
import { refreshTokens } from '../utils/api/auth';

const TokenProvider: React.FC<PropsWithChildren> = ({ children }) => {
  const [loading, { off: finishLoading }] = useBoolean(true);

  const [sessionToken, setSessionToken] = useState(initialState.sessionToken);
  const [userId, setUserId] = useState(initialState.userId);
  const [userType, setUserType] = useState(initialState.userType);

  const setSessionInfo = useCallback(
    (info: SessionInfo | undefined) => {
      if (!info) {
        setSessionToken(undefined);
        setUserId(undefined);
        setUserType(undefined);
      } else {
        setSessionToken(info.sessionToken);
        setUserId(info.userId);
        setUserType(info.userType);
      }
    },
    [setSessionToken, setUserId, setUserType]
  );

  useEffect(() => {
    const populateContext = async () => {
      try {
        const res = await refreshTokens();
        console.log('successfully refreshed', res);
        setSessionInfo({
          sessionToken: res.access_token,
          userId: res.user_id,
          userType: res.user_type
        });
      } catch (e) {
        console.log('error in refreshing tokens', e);
        setSessionInfo(undefined);
      }
      finishLoading();
    };

    populateContext();
  }, [setSessionInfo, finishLoading]);

  const getters = {
    sessionToken,
    userId,
    userType
  };

  const setters = {
    setSessionInfo
  };

  if (loading) {
    return (
      <Fade in={loading}>
        <Flex flexDir="column" height="100svh">
          <LoadingPage />
        </Flex>
      </Fade>
    );
  }

  return (
    <AuthContext.Provider value={{ getters, setters }}>
      <Fade in={!loading}>{children}</Fade>
    </AuthContext.Provider>
  );
};

export default TokenProvider;
