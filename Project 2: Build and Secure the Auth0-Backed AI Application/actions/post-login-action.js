/**
 * Auth0 Action — trigger: post-login
 * Paste this into Actions -> Library -> Build Custom -> (trigger: Login / Post Login),
 * click Deploy, then drag it into the Login flow under Actions -> Flows -> Login.
 *
 * Adds a custom "agent_id" claim to the ID token (and access token) so it
 * shows up when you decode the token at jwt.io.
 */
exports.onExecutePostLogin = async (event, api) => {
  // In a real system you'd look this up from event.user or your own DB.
  // Here we just derive a stable demo value from the user's id.
  const agentId = `agent-${event.user.user_id.slice(-8)}`;

  const namespace = "https://ai-agent-api/"; // must be a namespaced URI per Auth0 rules

  api.idToken.setCustomClaim(`${namespace}agent_id`, agentId);
  api.accessToken.setCustomClaim(`${namespace}agent_id`, agentId);
};