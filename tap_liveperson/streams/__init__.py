from tap_liveperson.streams.engagement_history import EngagementHistoryStream
from tap_liveperson.streams.messaging_interactions \
    import MessagingInteractionsStream
from tap_liveperson.streams.agent_activity \
    import AgentActivityStream
from tap_liveperson.streams.queue_health \
    import QueueHealthStream
from tap_liveperson.streams.agent_state_distribution \
    import AgentStateDistribution
from tap_liveperson.streams.messaging_queue_health \
    import MessagingQueueHealthStream

from tap_liveperson.streams.agent_groups import AgentGroupsStream
from tap_liveperson.streams.agent_status import AgentStatusStream
from tap_liveperson.streams.skills import SkillsStream
from tap_liveperson.streams.users import UsersStream

AVAILABLE_STREAMS = [
    AgentGroupsStream,
    AgentStatusStream,
    SkillsStream,
    UsersStream,
    EngagementHistoryStream,
    MessagingInteractionsStream,
    AgentActivityStream,
    QueueHealthStream,
    AgentStateDistribution,
    MessagingQueueHealthStream
]

__all__ = [
    'AgentGroupsStream',
    'AgentStatusStream',
    'SkillsStream',
    'UsersStream',
    'EngagementHistoryStream',
    'MessagingInteractionsStream',
    'AgentActivityStream',
    'QueueHealthStream',
    'AgentStateDistribution',
    'MessagingQueueHealthStream'
]
