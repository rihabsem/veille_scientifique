// App.jsx
import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
// import CompleteProfile from './CompleteProfile'
import LoginButton from './LoginButton'
import RegisterationForm from './RegistrationForm/RegistrationForm'

function App() {
  const { isAuthenticated, isLoading, user } = useAuth0();
  const [isNewUser, setIsNewUser] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user?.sub) {
      fetch(`/api/users/${user.sub}`)
        .then(res => {
          if (res.status === 404) {
            setIsNewUser(true);
          }
        });
    }
  }, [isAuthenticated, user]);

  if (isLoading) return <p>Loading...</p>;

  if (!isAuthenticated) return <LoginButton />; //si aucune session active
  if (isNewUser) {
    return <CompleteProfile user={user} />;
  }
  return <Dashboard />;
}

export default App

  
