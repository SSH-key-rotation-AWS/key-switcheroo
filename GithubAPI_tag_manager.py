from octokit import Octokit
from octokit import webhook
from octokit import actions

repos = Octokit().repos.get_for_org(org='octokit', type='public')
# Make an unauthenticated request for the public repositories of the octokit organization

