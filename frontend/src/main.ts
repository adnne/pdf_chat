import { createApp, type App as VueApp } from "vue";
import App from "./App.vue";
import router from "./router";
// Pinia imports
import { createPinia } from "pinia";

// PrimeVue imports
import PrimeVue from "primevue/config";
import "primevue/resources/themes/lara-light-blue/theme.css";
import "primevue/resources/primevue.min.css";
import "primeicons/primeicons.css";
import "primeflex/primeflex.css";

// PrimeVue components
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Card from "primevue/card";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import Divider from "primevue/divider";
import ScrollPanel from "primevue/scrollpanel";
import ProgressSpinner from "primevue/progressspinner";
import Message from "primevue/message";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";

const app = createApp(App);

// Use plugins
app.use(router);
app.use(PrimeVue);
app.use(ToastService);
app.use(createPinia());

// Register components
app.component("Button", Button);
app.component("InputText", InputText);
app.component("Textarea", Textarea);
app.component("Card", Card);
app.component("TabView", TabView);
app.component("TabPanel", TabPanel);
app.component("Divider", Divider);
app.component("ScrollPanel", ScrollPanel);
app.component("ProgressSpinner", ProgressSpinner);
app.component("Message", Message);
app.component("Toast", Toast);

app.mount("#app");
