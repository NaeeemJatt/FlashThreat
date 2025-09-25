# FlashThreat User Guide

## Getting Started

FlashThreat is a comprehensive threat intelligence analysis platform that helps security professionals analyze Indicators of Compromise (IOCs) against multiple threat intelligence sources.

### What is FlashThreat?

FlashThreat aggregates data from multiple threat intelligence providers to give you a unified view of potential threats. It supports analysis of:

- **IP Addresses** (IPv4 and IPv6)
- **Domain Names**
- **URLs**
- **File Hashes** (MD5, SHA1, SHA256)

### Supported Providers

- **VirusTotal**: Comprehensive threat intelligence for all IOC types
- **AbuseIPDB**: IP reputation and abuse reports
- **Shodan**: Network exposure and vulnerability information
- **AlienVault OTX**: Open Threat Exchange for all IOC types

## Using FlashThreat

### Single IOC Analysis

1. **Navigate to the Home page**
2. **Enter an IOC** in the search box:
   - IP address: `8.8.8.8`
   - Domain: `google.com`
   - URL: `https://example.com/malware.exe`
   - Hash: `d41d8cd98f00b204e9800998ecf8427e`
3. **Click "Check IOC"** to start the analysis
4. **View results** as they stream in from each provider

### Understanding Results

#### Verdict Types
- **🟢 Clean**: Low threat score, appears safe
- **🟡 Suspicious**: Moderate threat indicators
- **🔴 Malicious**: High threat score, confirmed malicious
- **⚪ Unknown**: Insufficient data for determination

#### Score Interpretation
- **0-19**: Clean
- **20-49**: Unknown
- **50-79**: Suspicious
- **80-100**: Malicious

#### Provider Results
Each provider shows:
- **Status**: Success/Error status
- **Reputation Score**: 0-100 scale
- **Detection Counts**: Malicious/Suspicious/Harmless detections
- **Evidence**: Detailed threat intelligence
- **Response Time**: API latency

### Bulk Analysis

1. **Navigate to the Bulk page**
2. **Prepare a CSV file** with IOCs:
   ```csv
   ioc,type
   8.8.8.8,ipv4
   google.com,domain
   https://example.com,url
   ```
3. **Upload the file** using the file picker
4. **Monitor progress** in real-time
5. **Download results** when complete

### History and Lookups

1. **Navigate to the History page**
2. **View past analyses** with search and filtering
3. **Click on any lookup** to see detailed results
4. **Add notes** to lookups for documentation

## Advanced Features

### Force Refresh
- Check the "Force Refresh" option to bypass cache
- Useful for getting the latest data from providers
- May take longer due to fresh API calls

### Real-time Streaming
- Results appear as they arrive from each provider
- No need to wait for all providers to complete
- Provides immediate feedback on IOC status

### Evidence Analysis
- Click on provider cards to expand evidence
- View detailed threat intelligence reports
- Access original provider links for more information

## Best Practices

### IOC Preparation
- **Clean your data**: Remove extra spaces and special characters
- **Validate formats**: Ensure IPs, domains, and URLs are properly formatted
- **Use appropriate types**: Match IOC types to analysis requirements

### Performance Optimization
- **Use caching**: Don't force refresh unless necessary
- **Batch processing**: Use bulk analysis for multiple IOCs
- **Monitor rate limits**: Be aware of API rate limits

### Security Considerations
- **Handle results carefully**: Malicious IOCs may contain sensitive information
- **Document findings**: Use notes feature to record analysis results
- **Follow organizational policies**: Adhere to your security team's guidelines

## Troubleshooting

### Common Issues

#### "Invalid IOC Format" Error
- **Check format**: Ensure IPs are valid, domains don't have protocols
- **Remove extra characters**: Clean URLs and file paths
- **Verify hash length**: MD5 (32 chars), SHA1 (40 chars), SHA256 (64 chars)

#### "Provider Unavailable" Error
- **Check network**: Ensure internet connectivity
- **Verify API keys**: Contact administrator if providers are down
- **Try again later**: Temporary provider issues may resolve

#### Slow Performance
- **Check cache**: Use cached results when possible
- **Monitor system**: Check system health page
- **Reduce batch size**: Process fewer IOCs at once

### Getting Help

#### System Health
- Navigate to the system health page
- Check component status
- Review performance metrics

#### Contact Support
- Check the API documentation
- Review error messages carefully
- Contact your system administrator

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Focus search box
- **Enter**: Submit IOC analysis
- **Escape**: Cancel ongoing analysis
- **Ctrl/Cmd + R**: Refresh page

## Mobile Usage

FlashThreat is optimized for mobile devices:
- **Touch-friendly interface**: Large buttons and touch targets
- **Responsive design**: Adapts to different screen sizes
- **Mobile navigation**: Easy access to all features
- **Offline indicators**: Clear status when connectivity is limited

## Security Features

### Input Validation
- **XSS Protection**: All inputs are sanitized
- **SQL Injection Prevention**: Database queries are protected
- **Rate Limiting**: Prevents abuse and ensures fair usage

### Data Protection
- **Encrypted Storage**: All data is encrypted at rest
- **Secure Transmission**: HTTPS for all communications
- **Access Control**: Role-based permissions

### Privacy
- **No Data Retention**: IOC data is not permanently stored
- **Audit Logging**: All actions are logged for security
- **Compliance**: Follows security best practices

## Tips for Security Analysts

### IOC Analysis Workflow
1. **Start with single IOC**: Get familiar with the interface
2. **Use bulk processing**: For large datasets
3. **Review evidence**: Don't rely solely on scores
4. **Document findings**: Use notes and export features
5. **Follow up**: Re-check IOCs periodically

### Threat Intelligence Integration
- **Export results**: Use CSV export for external tools
- **API integration**: Connect to other security tools
- **Automation**: Use API for automated analysis
- **Reporting**: Generate reports from analysis results

### Collaboration
- **Share results**: Use lookup IDs to share specific analyses
- **Team notes**: Add notes for team members
- **History tracking**: Review team analysis history
- **Knowledge sharing**: Build organizational threat intelligence

## Frequently Asked Questions

### Q: How accurate are the results?
A: FlashThreat aggregates data from multiple reputable providers. Results are weighted based on provider reliability and detection confidence.

### Q: Can I analyze private/internal IOCs?
A: Yes, but be aware that some providers may log or store IOC data. Check your organization's data handling policies.

### Q: How long are results cached?
A: Results are cached based on IOC type: IPs (1 hour), Domains (3 hours), URLs (3 hours), Hashes (7 days).

### Q: Can I integrate FlashThreat with other tools?
A: Yes, FlashThreat provides a comprehensive REST API for integration with other security tools and workflows.

### Q: What happens if a provider is down?
A: FlashThreat will continue to work with available providers. Results will indicate which providers were unavailable.

### Q: How do I get API access?
A: Contact your system administrator to obtain API credentials and access tokens.

## Support and Resources

- **API Documentation**: `/docs` endpoint for interactive API documentation
- **System Health**: Monitor system status and performance
- **User Manual**: This guide for end-user instructions
- **Developer Guide**: Technical documentation for developers
- **Community**: Check with your organization's security team

---

For technical support or feature requests, contact your system administrator or security team.
