from tap_liveperson.streams.engagement_history import EngagementHistoryStream
from tap_liveperson.streams.messaging_interactions \
    import MessagingInteractionsStream
from tap_liveperson.streams.agent_activity \
    import AgentActivityStream

from tap_liveperson.streams.agent_groups import AgentGroupsStream
from tap_liveperson.streams.agent_status import AgentStatusStream
from tap_liveperson.streams.skills import SkillsStream
from tap_liveperson.streams.users import UsersStream

AVAILABLE_STREAMS = [
    #AgentGroupsStream,
    #AgentStatusStream,
    #SkillsStream,
    #UsersStream,
    #EngagementHistoryStream,
    #MessagingInteractionsStream,
    AgentActivityStream
]

__all__ = [
    'AgentGroupsStream',
    'AgentStatusStream',
    'SkillsStream',
    'UsersStream',
    'EngagementHistoryStream',
    'MessagingInteractionsStream',
    'AgentActivityStream',
]
