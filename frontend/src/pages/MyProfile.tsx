import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState } from '@/store'
import { authApi } from '@/api/auth'
import { setUserData } from '@/store/slices/authSlice'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'react-toastify'

const profileSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
})

const passwordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: z.string().min(6, 'New password must be at least 6 characters'),
  confirmPassword: z.string().min(1, 'Please confirm your password'),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type ProfileFormValues = z.infer<typeof profileSchema>
type PasswordFormValues = z.infer<typeof passwordSchema>

const MyProfile = () => {
  const dispatch = useDispatch()
  const firstName = useSelector((state: RootState) => state.auth.firstName)
  const lastName = useSelector((state: RootState) => state.auth.lastName)
  const email = useSelector((state: RootState) => state.auth.email)
  
  const [isProfileLoading, setIsProfileLoading] = useState(false)
  const [isPasswordLoading, setIsPasswordLoading] = useState(false)

  const profileForm = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: firstName || '',
      lastName: lastName || '',
    },
  })

  const passwordForm = useForm<PasswordFormValues>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  })

  // Update form when Redux state changes
  useEffect(() => {
    const currentFirstName = profileForm.getValues('firstName')
    const currentLastName = profileForm.getValues('lastName')
    
    if ((firstName && firstName !== currentFirstName) || (lastName && lastName !== currentLastName)) {
      profileForm.reset({
        firstName: firstName || '',
        lastName: lastName || '',
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firstName, lastName])

  const onProfileSubmit = async (data: ProfileFormValues) => {
    setIsProfileLoading(true)
    try {
      const response = await authApi.updateProfile(data)
      dispatch(setUserData({
        email: response.email,
        firstName: response.firstName,
        lastName: response.lastName,
      }))
      toast.success('Profile updated successfully!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setIsProfileLoading(false)
    }
  }

  const onPasswordSubmit = async (data: PasswordFormValues) => {
    setIsPasswordLoading(true)
    try {
      await authApi.changePassword({
        currentPassword: data.currentPassword,
        newPassword: data.newPassword,
      })
      toast.success('Password changed successfully!')
      passwordForm.reset()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password')
    } finally {
      setIsPasswordLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">My Profile</h1>
          <p className="text-muted-foreground">Manage your profile settings.</p>
        </div>

        {/* Profile Update Section */}
        <div className="bg-card border rounded-lg p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-1">Profile Information</h2>
            <p className="text-sm text-muted-foreground">
              Update your first and last name
            </p>
          </div>

          <Form {...profileForm}>
            <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-4">
              <FormField
                control={profileForm.control}
                name="firstName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>First Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter your first name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={profileForm.control}
                name="lastName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Last Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter your last name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="pt-2">
                <Button type="submit" disabled={isProfileLoading}>
                  {isProfileLoading ? 'Updating...' : 'Update Profile'}
                </Button>
              </div>
            </form>
          </Form>
        </div>

        {/* Password Change Section */}
        <div className="bg-card border rounded-lg p-6 space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-1">Change Password</h2>
            <p className="text-sm text-muted-foreground">
              Update your password to keep your account secure
            </p>
          </div>

          <Form {...passwordForm}>
            <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
              <FormField
                control={passwordForm.control}
                name="currentPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Current Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Enter your current password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={passwordForm.control}
                name="newPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Enter your new password" {...field} />
                    </FormControl>
                    <FormDescription>
                      Password must be at least 6 characters long
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={passwordForm.control}
                name="confirmPassword"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Confirm New Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="Confirm your new password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="pt-2">
                <Button type="submit" disabled={isPasswordLoading}>
                  {isPasswordLoading ? 'Changing Password...' : 'Change Password'}
                </Button>
              </div>
            </form>
          </Form>
        </div>

        {/* Email Display (Read-only) */}
        <div className="bg-card border rounded-lg p-6">
          <div>
            <h2 className="text-xl font-semibold mb-1">Account Information</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Your account email address
            </p>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input value={email || ''} disabled className="bg-muted" />
              <p className="text-xs text-muted-foreground">
                Email cannot be changed
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MyProfile
