
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Link,
  Stack,
  Text,
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  IconButton,
  Flex,
  Divider,
  VStack,
  useToast,
  Checkbox,
  Image,
} from '@chakra-ui/react';
import { EyeIcon, EyeOffIcon, FacebookIcon, GithubIcon, TwitterIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{email?: string, password?: string}>({});
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useAuth();

  const validate = () => {
    const newErrors: {email?: string, password?: string} = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Demo login - in a real app this would validate with a backend
      if (email === 'user@example.com' && password === 'password') {
        login({
          id: '1',
          name: 'Demo User',
          email: 'user@example.com',
        });
        
        toast({
          title: 'Login successful',
          description: 'Welcome back!',
          status: 'success',
          duration: 3000,
          isClosable: true,
          position: 'top-right',
        });
        
        navigate('/');
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (error) {
      toast({
        title: 'Login failed',
        description: 'Invalid email or password',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top-right',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('user@example.com');
    setPassword('password');
  };

  return (
    <Container maxW="container.md" py={12}>
      <Box 
        borderRadius="xl" 
        overflow="hidden" 
        boxShadow="xl"
        bg="white"
      >
        <Flex direction={{ base: 'column', md: 'row' }}>
          <Box 
            bg="brand.500" 
            color="white" 
            p={8} 
            display={{ base: 'none', md: 'flex' }}
            width={{ md: '40%' }}
            flexDirection="column"
            justifyContent="center"
          >
            <Heading size="xl" mb={6}>Welcome Back</Heading>
            <Text fontSize="lg" mb={8}>Sign in to continue your shopping experience with our exclusive deals and personalized recommendations.</Text>
            <Box>
              <Image 
                src="https://images.unsplash.com/photo-1573855619003-97b4799dcd8b?q=80&w=1974&auto=format&fit=crop" 
                alt="Shopping" 
                borderRadius="md"
                opacity="0.9"
              />
            </Box>
          </Box>
          
          <VStack 
            spacing={6} 
            align="stretch" 
            p={{ base: 6, md: 8 }}
            width={{ md: '60%' }}
          >
            <Box display={{ base: 'block', md: 'none' }} textAlign="center" mb={4}>
              <Heading size="xl">Welcome Back</Heading>
              <Text mt={2} color="gray.500">
                Sign in to your account
              </Text>
            </Box>
            
            <form onSubmit={handleSubmit}>
              <Stack spacing={5}>
                <FormControl isInvalid={!!errors.email}>
                  <FormLabel>Email address</FormLabel>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    size="lg"
                    borderRadius="md"
                  />
                  <FormErrorMessage>{errors.email}</FormErrorMessage>
                </FormControl>
                
                <FormControl isInvalid={!!errors.password}>
                  <FormLabel>Password</FormLabel>
                  <InputGroup>
                    <Input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      size="lg"
                      borderRadius="md"
                    />
                    <InputRightElement width="3rem" h="full">
                      <IconButton
                        aria-label={showPassword ? "Hide password" : "Show password"}
                        h="1.75rem"
                        size="sm"
                        onClick={() => setShowPassword(!showPassword)}
                        icon={showPassword ? <EyeOffIcon size={16} /> : <EyeIcon size={16} />}
                        variant="ghost"
                      />
                    </InputRightElement>
                  </InputGroup>
                  <FormErrorMessage>{errors.password}</FormErrorMessage>
                </FormControl>
                
                <Flex justify="space-between" align="center">
                  <Checkbox colorScheme="brand">Remember me</Checkbox>
                  <Link color="brand.500" fontSize="sm" href="#">
                    Forgot password?
                  </Link>
                </Flex>
                
                <Button
                  type="submit"
                  colorScheme="brand"
                  size="lg"
                  fontSize="md"
                  isLoading={isSubmitting}
                  borderRadius="md"
                  boxShadow="md"
                  _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
                  transition="all 0.2s"
                >
                  Sign in
                </Button>

                <Button
                  variant="outline"
                  colorScheme="brand"
                  size="lg"
                  fontSize="md"
                  onClick={handleDemoLogin}
                  borderRadius="md"
                >
                  Use Demo Account
                </Button>
              </Stack>
            </form>
            
            <Flex align="center" my={4}>
              <Divider flex={1} />
              <Text px={3} color="gray.500" fontSize="sm">
                OR CONTINUE WITH
              </Text>
              <Divider flex={1} />
            </Flex>
            
            <Stack direction="row" spacing={4}>
              <Button w="full" leftIcon={<FacebookIcon size={20} />} colorScheme="facebook" variant="outline" borderRadius="md">
                Facebook
              </Button>
              <Button w="full" leftIcon={<TwitterIcon size={20} />} colorScheme="twitter" variant="outline" borderRadius="md">
                Twitter
              </Button>
            </Stack>
            
            <Box textAlign="center" mt={4}>
              <Text>
                Don't have an account?{' '}
                <Link as={RouterLink} to="/register" color="brand.500" fontWeight="semibold">
                  Sign up
                </Link>
              </Text>
            </Box>
          </VStack>
        </Flex>
      </Box>
    </Container>
  );
};

export default LoginPage;
