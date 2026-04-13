<template>
    <div class="login-page">
        <div class="login-shell">
            <section class="login-hero">
                <p class="eyebrow"></p>
                <h1>智能体登录</h1>
                <p class="subtitle">Enter your account details to access the dashboard and manage your workspace.</p>
            </section>

            <section class="login-card">
                <div class="field-group">
                    <label for="username">账号</label>
                    <input
                        id="username"
                        type="text"
                        placeholder="请输入账号"
                        v-model.trim="Username"
                        @focus="handleUsernameFocus"
                        @blur="handleUsernameBlur"
                        @input="handleUsernameInput"
                        :title="usernameMessage"
                    >
                </div>

                <div class="field-group">
                    <label for="password">密码</label>
                    <input
                        id="password"
                        type="password"
                        placeholder="请输入密码"
                        v-model="Password"
                        @focus="handlePasswordFocus"
                        @blur="handlePasswordBlur"
                        @input="handlePasswordInput"
                        :title="passwordMessage"
                    >
                </div>

                <div class="actions">
                    <button type="button" :disabled="isSubmitting || !canSubmit" @click="handleLogin">
                        <span v-if="!isSubmitting">Login</span>
                        <span v-else>正在验证...</span>
                    </button>
                </div>
            </section>
        </div>
    </div>
    <!-- <button @click="islogin">Check Login Status</button> -->
</template>
<script setup>
    import { computed, ref } from 'vue';
    import { useRouter } from 'vue-router';
    import { ElMessage } from 'element-plus';

    
    const router = useRouter();
    const Username = ref('');
    const Password = ref('');
    const isSubmitting = ref(false);
    const usernameTouched = ref(false);
    const passwordTouched = ref(false);
    const usernameFocused = ref(false);
    const passwordFocused = ref(false);
    const loginDelay = 900;

    const usernameError = computed(() => usernameTouched.value && !Username.value.trim());
    const passwordError = computed(() => passwordTouched.value && Password.value.length < 1);
    const canSubmit = computed(() => Username.value.trim().length > 0 && Password.value.length > 0);
    const usernameMessage = computed(() => {
        if (usernameError.value) {
            return '账号不能为空，请输入登录账号。';
        }
        if (usernameFocused.value || Username.value.trim()) {
            return '请输入你的账号。';
        }
        return '请输入你的账号。';
    });
    const passwordMessage = computed(() => {
        if (passwordError.value) {
            return '密码不能为空，请输入登录密码。';
        }
        if (passwordFocused.value || Password.value.length > 0) {
            return '请输入你的密码。';
        }
        return '请输入你的密码。';
    });

    const handleUsernameBlur = () => {
        usernameFocused.value = false;
        usernameTouched.value = true;
    };

    const handleUsernameFocus = () => {
        usernameFocused.value = true;
        if (!Username.value.trim()) {
            ElMessage.info('请输入登录账号，例如 admin123');
        }
    };

    const handlePasswordBlur = () => {
        passwordFocused.value = false;
        passwordTouched.value = true;
    };

    const handlePasswordFocus = () => {
        passwordFocused.value = true;
        if (!Password.value) {
            ElMessage.info('请输入登录密码');
        }
    };

    const handleUsernameInput = () => {
        usernameTouched.value = true;
    };

    const handlePasswordInput = () => {
        passwordTouched.value = true;
    };

    //登录
    const handleLogin = async () =>{
        console.log("username: " + Username.value);
        console.log("password: " + Password.value);

        usernameTouched.value = true;
        passwordTouched.value = true;

        if (!canSubmit.value) {
            ElMessage.warning('请先输入账号和密码');
            return;
        }

        isSubmitting.value = true;
        ElMessage.info('正在验证账号信息，请稍候...');
        try{
            const response = await fetch('http://localhost:8080/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username: Username.value,
                    password: Password.value
                })
            });

            const data = await response.json();
            console.log('Response data:', data);
            console.log("message",data.msg);
            
            if(data.msg =='登录成功'){
                localStorage.setItem('user-role', data.role);
                console.log('user-role',data.role);

                localStorage.setItem('username', data.username);
                console.log('username:', data.username);
                
                console.log('Login successful:', response);
                localStorage.setItem('sa-token', data.token);
                console.log('sa-token:', data.token);
                
                localStorage.setItem('user-perms',JSON.stringify(data.perms));
                console.log('user-perms:', data.perms);

                ElMessage.success('登录成功，正在跳转');

                setTimeout(async () => {
                    await router.push({ name: 'home' });
                }, loginDelay);
                

            } else {
                ElMessage.error(data.msg || '登录失败');
                console.error('Login failed:', response.statusText);
            }
        } catch (error) {
            ElMessage.error('登录请求失败');
            console.error('Login error:', error);

        } finally {
            isSubmitting.value = false;
        }
    }
    const islogin = async () => {
        try {
            const response = await fetch('http://localhost:8080/api/islogin', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            console.log('Current user data:', data);

        }catch(error){
            console.error('Error fetching current user data:', error);
        }
    }
</script>

<style scoped>
.login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.28), transparent 32%),
        radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.22), transparent 30%),
        linear-gradient(135deg, #0f172a 0%, #111827 45%, #1e293b 100%);
}

.login-shell {
    width: min(960px, 100%);
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 28px;
    background: rgba(15, 23, 42, 0.72);
    box-shadow: 0 24px 80px rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(18px);
    animation: floatIn 0.8s ease both;
}

.login-hero {
    padding: 56px;
    color: #e2e8f0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 18px;
    background:
        linear-gradient(160deg, rgba(15, 118, 110, 0.18), rgba(59, 130, 246, 0.08)),
        radial-gradient(circle at top right, rgba(34, 197, 94, 0.18), transparent 35%);
}

.eyebrow {
    margin: 0;
    display: inline-flex;
    align-self: flex-start;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.14);
    color: #93c5fd;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

.login-hero h1 {
    margin: 0;
    font-size: clamp(2rem, 4vw, 3.4rem);
    line-height: 1.05;
    max-width: 12ch;
}

.subtitle {
    margin: 0;
    max-width: 38ch;
    font-size: 1rem;
    line-height: 1.8;
    color: #cbd5e1;
}

.login-card {
    padding: 56px 44px;
    background: rgba(15, 23, 42, 0.8);
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 20px;
}

.field-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.field-group label {
    color: #e2e8f0;
    font-size: 0.95rem;
    font-weight: 600;
}

.field-group input {
    width: 100%;
    padding: 15px 16px;
    border: 1px solid rgba(148, 163, 184, 0.28);
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.72);
    color: #f8fafc;
    font-size: 1rem;
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.field-group input::placeholder {
    color: #94a3b8;
}

.field-group input:focus {
    border-color: rgba(96, 165, 250, 0.9);
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.18);
    transform: translateY(-1px);
}

.actions {
    margin-top: 8px;
}

.actions button {
    width: 100%;
    padding: 14px 18px;
    border: none;
    border-radius: 14px;
    background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%);
    color: #ffffff;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
    box-shadow: 0 14px 28px rgba(37, 99, 235, 0.35);
}

.actions button:disabled {
    cursor: not-allowed;
    opacity: 0.72;
    transform: none;
    box-shadow: 0 10px 20px rgba(37, 99, 235, 0.18);
}

.actions button:hover {
    transform: translateY(-1px);
    filter: brightness(1.05);
    box-shadow: 0 18px 34px rgba(37, 99, 235, 0.42);
}

.actions button:active {
    transform: translateY(0);
}

@media (max-width: 840px) {
    .login-shell {
        grid-template-columns: 1fr;
    }

    .login-hero,
    .login-card {
        padding: 32px 24px;
    }

    .login-card {
        border-left: none;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
}
</style>