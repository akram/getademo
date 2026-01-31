# Kagenti Platform Walkthrough Demo Script

## Demo Overview
- **Duration**: ~3-4 minutes
- **Target**: Kagenti UI deployed on OpenShift
- **URL**: https://kagenti-ui-mschimun.apps.rosa.mschimun.072j.p3.openshiftapps.com/

---

## Step 1: Introduction & Home Page
**Duration**: ~25 seconds

**Narration**:
"Welcome to Kagenti, the Cloud Native Agent Platform. Kagenti provides a framework-neutral, scalable, and secure platform for deploying and orchestrating AI agents. Let's explore the main functionalities of the platform."

**Visual**: Home page showing the welcome message and overview sections

**Actions**:
1. Show the home page with welcome message
2. Highlight the Key Sections on the left
3. Show Monitoring & Administration on the right

---

## Step 2: Agent Catalog Overview
**Duration**: ~30 seconds

**Narration**:
"The Agent Catalog is where you can browse, interact with, and manage your deployed AI agents. Here we can see agents deployed in the agentic-workloads namespace. Each agent shows its description, status, framework, and protocol type. The agents shown here support the A2A protocol - that's Agent-to-Agent communication."

**Visual**: Agent Catalog page showing the list of agents

**Actions**:
1. Navigate to Agent Catalog
2. Show the namespace selector
3. Highlight the two agents: mcp-agent-ui and orchestrator-agent-ui
4. Point out the tags showing framework: kagent and protocol: a2a

---

## Step 3: Agent Details & Chat Interface
**Duration**: ~35 seconds

**Narration**:
"Let's view the details of the MCP agent. Here we can see the agent's URL, description, and its capabilities. The agent supports streaming and state transition history. Under Skills, we can see this agent has GitHub Operations capability - it can search and retrieve GitHub repository information. At the bottom, there's a Chat with Agent interface where you can interact directly with the agent."

**Visual**: Agent details page with expanded Capabilities & Skills sections

**Actions**:
1. Click View Details on mcp-agent-ui
2. Expand Capabilities & Modes section
3. Expand Skills section
4. Show the Chat with Agent interface

---

## Step 4: Import New Agent
**Duration**: ~30 seconds

**Narration**:
"To deploy a new agent, navigate to Import New Agent. You can select the target Kubernetes namespace and configure the pod settings including service ports. Kagenti supports two deployment methods: Build from Source, which builds directly from a Git repository, or Deploy from Existing Image using a pre-built container. This makes it easy to bring agents from any framework into the platform."

**Visual**: Import New Agent page showing configuration options

**Actions**:
1. Navigate to Import New Agent
2. Show the namespace selector
3. Highlight Kubernetes Pod Configuration
4. Show Deployment Method options

---

## Step 5: Observability Dashboard
**Duration**: ~30 seconds

**Narration**:
"The Observability Dashboard provides comprehensive monitoring for your agents. You can access Phoenix and OpenTelemetry for tracing and performance monitoring, Kiali for visualizing network traffic and service mesh interactions, and the MCP Gateway Inspector for exploring federated tools. These integrations give you full visibility into how your agents are performing and communicating."

**Visual**: Observability Dashboard showing all monitoring options

**Actions**:
1. Navigate to Observability
2. Show Tracing & Performance Monitoring section
3. Show Network Traffic & Service Mesh section
4. Show MCP Gateway Access section

---

## Step 6: Conclusion
**Duration**: ~15 seconds

**Narration**:
"That's a quick tour of the Kagenti platform. From deploying agents to monitoring their performance, Kagenti provides all the tools you need to run AI agents in production. Visit kagenti.io to learn more."

**Visual**: Return to Home page

**Actions**:
1. Navigate back to Home
2. Pause on the welcome page

---

## Technical Notes

### Pre-Recording Setup
- Browser zoom: 125% for better viewport fill
- Resolution: 1920x1080
- Use window capture mode for Chromium

### Key Features to Highlight
1. **Agent Catalog**: Browse and manage deployed agents
2. **Chat with Agent**: Interactive agent testing
3. **Import New Agent**: Deploy from source or existing images
4. **Observability**: Phoenix, Kiali, MCP Gateway integration
5. **A2A Protocol**: Agent-to-Agent communication standard







